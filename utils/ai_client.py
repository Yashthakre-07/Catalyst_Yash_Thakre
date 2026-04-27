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
        self.nvidia_keys = self._discover_keys("NVIDIA_API_KEY")
        
        self.gemini_model_name = settings.GEMINI_MODEL
        self.groq_model_name = settings.GROQ_MODEL
        self.nvidia_model_name = settings.NVIDIA_MODEL
        
        # Build the final sorted pool based on primary provider
        gemini_items = [("gemini", k) for k in self.gemini_keys]
        groq_items = [("groq", k) for k in self.groq_keys]
        nvidia_items = [("nvidia", k) for k in self.nvidia_keys]
        
        if self.primary_provider == "gemini":
            self.all_keys = gemini_items + groq_items + nvidia_items
        elif self.primary_provider == "nvidia":
            self.all_keys = nvidia_items + gemini_items + groq_items
        else:
            self.all_keys = groq_items + gemini_items + nvidia_items
        
        if not self.all_keys:
            logger.error("No API keys discovered!")

    def _discover_keys(self, prefix: str) -> list[str]:
        import os
        st_secrets = {}
        try:
            import streamlit as st
            try:
                # We try to convert to dict to trigger the parse early and catch any errors
                st_secrets = dict(st.secrets)
            except:
                st_secrets = {}
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
                cleaned_val = str(val).strip().replace('"', '').replace("'", "")
                keys.append(cleaned_val)
        return list(dict.fromkeys(keys)) # Remove duplicates

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None,
        json_mode: bool = False
    ) -> Optional[str]:
        provider = provider_override or self.primary_provider
        
        try:
            if provider == "gemini":
                if api_key_override:
                    genai.configure(api_key=api_key_override)
                elif self.gemini_keys:
                    genai.configure(api_key=self.gemini_keys[0])
                else:
                    raise ValueError("No Gemini keys")
                    
                model = genai.GenerativeModel(
                    model_name=self.gemini_model_name,
                    system_instruction=system_prompt,
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                )
                response = model.generate_content(user_message, generation_config={"temperature": temperature, "max_output_tokens": max_tokens})
                return response.text
                
            elif provider == "groq":
                key = api_key_override or (self.groq_keys[0] if self.groq_keys else None)
                if not key: raise ValueError("No Groq keys")
                client = Groq(api_key=key)
                response = client.chat.completions.create(
                    model=self.groq_model_name,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                    temperature=temperature, max_tokens=max_tokens
                )
                return response.choices[0].message.content

            elif provider == "nvidia":
                key = api_key_override or (self.nvidia_keys[0] if self.nvidia_keys else None)
                if not key: raise ValueError("No NVIDIA keys")
                return self._complete_nvidia(key, system_prompt, user_message, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"AIClient Error ({provider}): {e}")
            raise e
            
        return None

    def _complete_nvidia(self, api_key, system_prompt, user_prompt, temperature, max_tokens):
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.nvidia_model_name,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": temperature, "max_tokens": max_tokens, "stream": False
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200: raise Exception(f"NVIDIA Error: {response.text}")
        return response.json()["choices"][0]["message"]["content"]

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
        num_keys = len(self.all_keys)
        
        for attempt in range(max_retries):
            current_idx = AIClient._global_rotation_idx % num_keys
            provider, key = self.all_keys[current_idx]
            
            if time.time() < AIClient._key_cool_downs.get(key, 0):
                AIClient._global_rotation_idx += 1
                continue

            try:
                logger.info(f"Attempt {attempt+1}: {provider} (Key {current_idx+1}/{num_keys})")
                raw = self.complete(system_prompt, user_message, temperature, max_tokens, provider_override=provider, api_key_override=key)
                
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
                if any(x in err_str for x in ["429", "rate", "quota", "exhausted", "limit"]):
                    AIClient._key_cool_downs[key] = time.time() + 90
                AIClient._global_rotation_idx += 1
                continue
                
        raise RuntimeError(f"CRITICAL: All {num_keys} keys exhausted. Check your API quotas.")
