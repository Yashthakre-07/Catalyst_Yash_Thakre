import os
import json
import fitz  # PyMuPDF
from loguru import logger
from typing import Optional

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file using PyMuPDF.
    
    Args:
        file_bytes: The raw byte content of the PDF.
        
    Returns:
        The extracted text as a single string.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return ""

def save_json_to_file(data: dict, filename: str) -> Optional[str]:
    """
    Saves a dictionary as a JSON file in the outputs/ directory.
    
    Args:
        data: The dictionary to save.
        filename: The desired filename (e.g., 'learning_plan.json').
        
    Returns:
        The full path to the saved file, or None if it failed.
    """
    try:
        os.makedirs("outputs", exist_ok=True)
        filepath = os.path.join("outputs", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        return filepath
    except Exception as e:
        logger.error(f"Failed to save JSON to {filename}: {e}")
        return None
