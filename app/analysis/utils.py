import pdfplumber
from PIL import Image, UnidentifiedImageError
import google.generativeai as genai
import os
import json
import re

def clean_json_response(text):
    """Extracts JSON object from a string that might contain Markdown or other text."""
    # Find the first '{' and the last '}'
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def pdf_to_images(pdf_path):
    """Converts the first page of a PDF to a PIL Image."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                # Get the first page
                page = pdf.pages[0]
                # Convert to image with high resolution for better OCR
                return page.to_image(resolution=300).original
    except Exception as e:
        print(f"PDF Error: {e}")
        return None
    return None

def analyze_medical_image(image_path, mime_type):
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("API Key missing")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Load image based on type
    img_data = None
    try:
        if mime_type == 'application/pdf':
            img_data = pdf_to_images(image_path)
            if img_data is None:
                return {"is_medical_report": False, "error": "Could not read PDF content. It might be corrupted or password protected."}
        else:
            # Verify it's a valid image
            try:
                with Image.open(image_path) as img:
                    img.verify()
                # Re-open for processing
                img_data = Image.open(image_path)
            except (UnidentifiedImageError, IOError):
                return {"is_medical_report": False, "error": "Invalid or corrupted image file."}
    except Exception as e:
        return {"is_medical_report": False, "error": f"File processing error: {str(e)}"}

    # Prompt Engineering: Chain of Thought & Structure Enforcement
    prompt = """
    You are an expert medical analyst. Analyze the provided document.

    CRITICAL INSTRUCTION: NO HALLUCINATIONS.
    - If a value is illegible, ambiguous, or missing, return "N/A" or null. DO NOT GUESS.
    - Do not make up test names or results that are not clearly visible in the document.
    - If the document is blurry or unreadable, state that in the error field.

    Task 1: Validation
    Determine if the document is a valid medical report (lab results, blood test, clinical notes, etc.).
    If it is NOT a medical report (e.g., a random image, invoice, non-medical text), return JSON with "is_medical_report": false.

    If it IS a medical report, proceed to extract the data.

    Task 2: Extraction
    Extract the patient name (if any), date, and all test results presented in tables or lists.
    Capture the Test Name, Result Value, Unit, and Reference Range.
    
    Task 3: Analysis
    Compare each result to its reference range. Flag it as 'High', 'Low', or 'Normal'.
    
    Task 4: Insight Generation
    For every result flagged as High or Low, provide a 'Simplified Insight'. 
    Explain in plain English what this abnormality usually implies (e.g., "Low Iron may indicate anemia").

    Task 5: Summary & Recommendations
    Provide a concise 'summary' of the overall health status based on the report.
    Provide a list of 'recommendations' (lifestyle, diet, or follow-up questions) based on the findings.
    
    Task 6: Output Format
    Return ONLY valid JSON matching this structure.
    
    Scenario 1: Valid Medical Report
    {
        "is_medical_report": true,
        "patient_name": "string",
        "date": "string",
        "summary": "string",
        "recommendations": ["string", "string"],
        "tests": [
            {
                "name": "string",
                "value": "string",
                "unit": "string",
                "range": "string",
                "status": "Normal/High/Low",
                "insight": "string (or null if normal)"
            }
        ]
    }

    Scenario 2: Invalid/Non-Medical Document
    {
        "is_medical_report": false,
        "error": "This document does not appear to be a medical report. Please upload a valid lab result or clinical record."
    }
    """
    
    try:
        response = model.generate_content([prompt, img_data])
        # Clean response to ensure it's pure JSON
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except json.JSONDecodeError:
        print(f"AI JSON Error: {response.text}")
        return {"is_medical_report": False, "error": "AI analysis failed to produce valid data. Please try again."}
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def reanalyze_medical_data(data):
    """
    Re-analyzes the medical data after user manual corrections.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("API Key missing")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are an expert medical analyst. The user has manually verified and corrected the following medical test results.
    
    Please re-analyze this data.
    1. Re-evaluate the 'status' (High/Low/Normal) for each test based on the value and range.
    2. Generate new 'insight' for abnormal results.
    3. Generate a new 'summary' and 'recommendations' based on the corrected data.
    
    Input Data:
    {json.dumps(data)}

    Output Format:
    Return ONLY valid JSON matching the same structure as the input, but with updated analysis fields (status, insight, summary, recommendations).
    Keep the patient_name, date, and test values/units/ranges as provided by the user (unless the range format needs standardization).
    """

    try:
        response = model.generate_content(prompt)
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except Exception as e:
        print(f"Re-analysis Error: {e}")
        return data # Return original data if re-analysis fails