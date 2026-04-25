import json
import os
from loguru import logger
from typing import List, Dict

def load_resources() -> Dict[str, List[Dict]]:
    """Loads the skill resources from the JSON file."""
    filepath = os.path.join("data", "skill_resources.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Normalize keys to lowercase for easier matching
            return {k.lower(): v for k, v in data.items()}
    except FileNotFoundError:
        logger.warning(f"Resource file not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error parsing resource file at {filepath}")
        return {}

def find_resources_for_skills(skill_names: List[str]) -> Dict[str, List[Dict]]:
    """
    Finds resources for a list of skills.
    
    Args:
        skill_names: List of skill names to find resources for.
        
    Returns:
        A dictionary mapping skill names to a list of resource dictionaries.
    """
    resources = load_resources()
    result = {}
    
    for skill in skill_names:
        normalized_skill = skill.lower()
        if normalized_skill in resources:
            result[skill] = resources[normalized_skill]
        else:
            # Simple fuzzy matching / substring check
            found = False
            for r_key, r_value in resources.items():
                if r_key in normalized_skill or normalized_skill in r_key:
                    result[skill] = r_value
                    found = True
                    break
            
            if not found:
                result[skill] = []
                
    return result
