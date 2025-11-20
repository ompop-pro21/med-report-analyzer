import google.generativeai as genai
import os
import json
import re

def clean_json_response(text):
    """Extracts JSON object from a string that might contain Markdown or other text."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def get_drug_info_from_ai(query):
    """
    Uses Gemini to find the generic name and standard brand name for a given drug query.
    This helps map common names like 'Paracetamol' to 'Acetaminophen'.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a pharmaceutical expert. The user is searching for a drug using the term: "{query}".
    
    Task:
    1. Identify the active ingredient (generic name) for this drug.
    2. Identify the most common US brand name associated with this generic (if different).
    3. Provide a brief 1-sentence description of what it treats.
    
    Output JSON ONLY:
    {{
        "generic_name": "string (e.g., acetaminophen)",
        "brand_name": "string (e.g., Tylenol)",
        "description": "string"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except Exception as e:
        print(f"AI Drug Search Error: {e}")
        return None
