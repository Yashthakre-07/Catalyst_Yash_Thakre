import time
from typing import Optional
from loguru import logger
import google.generativeai as genai
from groq import Groq
import groq
from config import settings
from google.api_core import exceptions as google_exceptions
import re
import json

class AIClient:
    """
    Unified wrapper around Gemini and Groq APIs with multi-key rotation and automatic failover.
    Scans environment for all available keys (e.g. GEMINI_API_KEY, GEMINI_API_KEY1, etc.)
    """
    
    # Static variable to remember rotation position across all instances
    _global_rotation_idx = 0
    _key_cool_downs = {} # Maps key -> timestamp when it becomes available again
    
    def __init__(self, provider: str = None):
        self.primary_provider = provider or settings.AI_PROVIDER
        self.current_provider = self.primary_provider
        
        # Key Pools
        self.gemini_keys = self._discover_keys("GEMINI_API_KEY")
        self.groq_keys = self._discover_keys("GROQ_API_KEY")
        
        self.gemini_model_name = settings.GEMINI_MODEL
        self.groq_model_name = settings.GROQ_MODEL
        
        # Build the final sorted pool based on primary provider
        gemini_items = [("gemini", k) for k in self.gemini_keys]
        groq_items = [("groq", k) for k in self.groq_keys]
        
        if self.primary_provider == "gemini":
            self.all_keys = gemini_items + groq_items
        else:
            self.all_keys = groq_items + gemini_items
        
        if not self.all_keys:
            logger.error("No API keys discovered!")

    def _discover_keys(self, prefix: str) -> list[str]:
        import os
        try:
            import streamlit as st
            st_secrets = st.secrets
        except:
            st_secrets = {}

        keys = []
        # Check index 0 (the base key) and 1-10
        for i in range(11):
            env_key = f"{prefix}{i}" if i > 0 else prefix
            
            # Try environment variable first
            val = os.getenv(env_key)
            
            # If not found, try Streamlit secrets
            if not val and env_key in st_secrets:
                val = st_secrets[env_key]
                
            if val:
                # CLEANING: Remove any accidental quotes or spaces
                cleaned_val = val.strip().replace('"', '').replace("'", "")
                keys.append(cleaned_val)
        return list(dict.fromkeys(keys)) # Remove duplicates

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        provider_override: str = None,
        api_key_override: str = None
    ) -> str:
        provider = provider_override or self.current_provider
        
        if provider == "gemini":
            if api_key_override:
                key = api_key_override
            elif self.gemini_keys:
                key = self.gemini_keys[0]
            else:
                raise ValueError("No Gemini API keys available.")
                
            genai.configure(api_key=key)
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                model_name=self.gemini_model_name,
                system_instruction=system_prompt,
                safety_settings=safety_settings
            )
            
            try:
                response = model.generate_content(
                    user_message,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )
                if not response:
                    raise ValueError("Gemini returned an empty response object.")
                try:
                    return response.text
                except ValueError:
                    # Handle safety blocks or empty candidates
                    if hasattr(response, 'candidates') and response.candidates:
                        reason = response.candidates[0].finish_reason
                        # If it was blocked, we might want to know why
                        block_msg = f"Gemini block/stop. Reason: {reason}"
                        if hasattr(response.candidates[0], 'safety_ratings'):
                            ratings = response.candidates[0].safety_ratings
                            block_msg += f" Safety: {ratings}"
                        raise ValueError(block_msg)
                    raise ValueError("Gemini response.text failed (likely safety block or empty response).")
            except Exception as e:
                raise e

        elif provider == "groq":
            if api_key_override:
                key = api_key_override
            elif self.groq_keys:
                key = self.groq_keys[0]
            else:
                raise ValueError("No Groq API keys available.")
                
            client = Groq(api_key=key)
            try:
                response = client.chat.completions.create(
                    model=self.groq_model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            except Exception as e:
                raise e
        
        raise ValueError(f"Unknown provider: {provider}")

    def _extract_json(self, text: str) -> str:
        first_brace = text.find('{')
        first_bracket = text.find('[')
        start = -1
        if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
            start = first_brace
            end = text.rfind('}')
        elif first_bracket != -1:
            start = first_bracket
            end = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return text.strip()

    def complete_with_retry(
        self,
        system_prompt: str,
        user_message: str,
        max_retries: int = 15,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        is_json: bool = True,
        **kwargs
    ) -> str:
        if not self.all_keys: raise RuntimeError("No API keys configured.")
            
        error_history = []
        num_keys = len(self.all_keys)
        
        for attempt in range(max_retries):
            # Scan for a key that isn't on cooldown
            current_idx = AIClient._global_rotation_idx % num_keys
            provider, key = self.all_keys[current_idx]
            
            # If this key is on cooldown, skip it immediately
            if time.time() < AIClient._key_cool_downs.get(key, 0):
                AIClient._global_rotation_idx += 1
                continue

            try:
                logger.info(f"Attempt {attempt+1}: {provider} (Key {current_idx+1}/{num_keys})")
                raw = self.complete(system_prompt, user_message, temperature, 
                                   max_tokens=max_tokens,
                                   provider_override=provider, api_key_override=key)
                
                if not raw:
                    AIClient._global_rotation_idx += 1
                    continue

                if is_json:
                    stripped = self._extract_json(raw)
                    try:
                        json.loads(stripped)
                        return stripped
                    except json.JSONDecodeError:
                        AIClient._global_rotation_idx += 1
                        continue
                
                return raw.strip()
                
            except Exception as e:
                err_str = str(e).lower()
                logger.warning(f"Key {current_idx+1} failed: {err_str[:100]}")
                
                # Mark for cooldown if it's a rate limit/quota error
                if any(x in err_str for x in ["429", "rate", "quota", "exhausted", "limit"]):
                    AIClient._key_cool_downs[key] = time.time() + 90 # 90s cooldown
                
                AIClient._global_rotation_idx += 1
                # No sleep here - just try the next key immediately!
                continue
                
        raise RuntimeError(f"CRITICAL: All {num_keys} keys exhausted after {max_retries} attempts. Check your API quotas.")
