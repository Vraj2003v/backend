import io
import datetime
import os
from PIL import Image
from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import helper functions
from utils.analysis import (
    extract_detected_plant,
    generate_identification,
    generate_disease_detection,
    create_pdf_report
)
from utils.image_processing import process_uploaded_image

app = Flask(__name__)

# Load API Key from .env
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Make sure `.env` file contains `GEMINI_API_KEY`.")

# Configure Google Generative AI Model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Store past analysis results
archive = []

def save_analysis_to_archive(image_name: str, analysis: str, image_data: bytes, detected_plant: str):
    """Save analysis results for later retrieval."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "id": len(archive) + 1,
        "timestamp": timestamp,
        "image_name": image_name,
        "analysis": analysis,
        "image_data": image_data,
        "detected_plant": detected_plant
    }
    archive.append(entry)
    return entry

@app.route("/", methods=["GET"])
def index():
    """Check if the backend is running."""
    return jsonify({"message": "PlantCare backend is running."})

@app.route("/api/identify", methods=["POST"])
def api_identify():
    """Identify a plant from an image."""
    if "plant_image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["plant_image"]
    image_data = process_uploaded_image(file)
    if not image_data:
        return jsonify({"error": "Failed to process image"}), 500

    try:
        analysis = generate_identification(image_data, model)
        if not analysis:
            return jsonify({"error": "Failed to analyze image"}), 500

        detected_plant = extract_detected_plant(analysis)
        entry = save_analysis_to_archive(file.filename, analysis, image_data["data"], detected_plant)

        return jsonify({
            "analysis": analysis,
            "detected_plant": detected_plant,
            "analysis_id": entry["id"]
        })

    except Exception as e:
        print(f"Error during plant identification: {str(e)}")
        return jsonify({"error": "Internal server error during analysis"}), 500

@app.route("/api/disease", methods=["POST"])
def api_disease():
    """Detect plant disease from an image."""
    if "plant_image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["plant_image"]
    image_data = process_uploaded_image(file)
    if not image_data:
        return jsonify({"error": "Failed to process image"}), 500

    try:
        analysis = generate_disease_detection(image_data, model)
        if not analysis:
            return jsonify({"error": "Failed to analyze image"}), 500

        detected_plant = extract_detected_plant(analysis)
        entry = save_analysis_to_archive(file.filename, analysis, image_data["data"], detected_plant)

        return jsonify({
            "analysis": analysis,
            "detected_plant": detected_plant,
            "analysis_id": entry["id"]
        })

    except Exception as e:
        print(f"Error during disease detection: {str(e)}")
        return jsonify({"error": "Internal server error during disease analysis"}), 500

@app.route("/download/pdf")
def download_pdf():
    """Download analysis as a PDF."""
    analysis_id = request.args.get("analysis_id", type=int)
    entry = next((item for item in archive if item["id"] == analysis_id), None)

    if entry:
        try:
            image = Image.open(io.BytesIO(entry["image_data"]))
            pdf_bytes = create_pdf_report(image, entry["analysis"])
            return send_file(io.BytesIO(pdf_bytes), as_attachment=True, download_name=f"plant_analysis_{analysis_id}.pdf", mimetype="application/pdf")

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return "Failed to generate PDF", 500

    return "Analysis not found", 404

if __name__ == "__main__":
    app.run(debug=True)
