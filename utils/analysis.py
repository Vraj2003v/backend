import io
import datetime
import os
from PIL import Image
from fpdf import FPDF

# Structured AI prompts to ensure distinct outputs
IDENTIFICATION_PROMPT = """
Identify the plant in this image. 
Provide the following details:
1. **Scientific Name** and **Common Name**
2. **Basic Description** of the plant
3. **Ideal Growing Conditions** (light, soil, water needs)
4. **General Care Instructions**
"""

DISEASE_DETECTION_PROMPT = """
Analyze the plant in this image for diseases. 
Provide the following details:
1. **Detected Disease Name** (if any)
2. **Symptoms & Causes** of the issue
3. **Recommended Prevention Methods**
4. **Treatment & Cure Steps** (if applicable)
"""

def clean_analysis(text: str) -> str:
    """Cleans unnecessary text from AI response for better readability."""
    unwanted_phrases = [
        "Okay, let's analyze this plant and figure out what's going on.",
        "Good luck! This will take some effort, but with careful attention, you can hopefully save the plant."
    ]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")
    return text.strip()

def extract_detected_plant(text: str) -> str:
    """Extracts detected plant name from AI-generated text."""
    marker = "Detected Plant:"
    lower_text = text.lower()
    if marker.lower() in lower_text:
        start = lower_text.find(marker.lower())
        extracted_line = text[start:].split("\n")[0]
        if ":" in extracted_line:
            return extracted_line.split(":", 1)[1].strip()
    return "Not Detected"

def create_pdf_report(image: Image.Image, analysis: str) -> bytes:
    """Generates a PDF report with analysis results and plant image."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "PlantCare AI Analysis Report", ln=True, align="C")
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="R")

        # Convert and embed image in PDF
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        temp_img_path = "temp_image.png"
        image.save(temp_img_path, "PNG", optimize=True)
        pdf.image(temp_img_path, x=10, w=190)
        os.remove(temp_img_path)

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Analysis Results", ln=True)
        pdf.set_font("Arial", "", 11)

        # Add formatted text
        for paragraph in analysis.split("\n"):
            if paragraph.strip():
                if paragraph.strip().isupper() or paragraph.startswith("#"):
                    pdf.set_font("Arial", "B", 12)
                    pdf.ln(5)
                    pdf.cell(0, 10, paragraph.strip(), ln=True)
                    pdf.set_font("Arial", "", 11)
                else:
                    pdf.multi_cell(0, 6, paragraph.strip())
                    pdf.ln(2)

        return pdf.output(dest="S").encode("latin-1", errors="replace")
    
    except Exception as e:
        print("Error generating PDF:", str(e))
        return b""

def generate_identification(image_data: dict, model) -> str:
    """Uses AI model to identify plant species."""
    try:
        image_pil = Image.open(io.BytesIO(image_data["data"]))

        if model is None:
            raise ValueError("AI model is not initialized.")

        response = model.generate_content([IDENTIFICATION_PROMPT, image_pil])

        if not response or not hasattr(response, "text") or not response.text.strip():
            return "Error: No plant identification result available."

        return clean_analysis(response.text)

    except Exception as e:
        print("Plant Identification Error:", str(e))
        return "Error: Unable to identify the plant."

def generate_disease_detection(image_data: dict, model) -> str:
    """Uses AI model to detect plant disease and recommend solutions."""
    try:
        image_pil = Image.open(io.BytesIO(image_data["data"]))

        if model is None:
            raise ValueError("AI model is not initialized.")

        response = model.generate_content([DISEASE_DETECTION_PROMPT, image_pil])

        if not response or not hasattr(response, "text") or not response.text.strip():
            return "Error: No disease detection result available."

        return clean_analysis(response.text)

    except Exception as e:
        print("Disease Detection Error:", str(e))
        return "Error: Unable to detect disease."
