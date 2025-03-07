import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    DEBUG = True
    API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
    
    # Use an environment variable to override the default model name if needed.
    MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
