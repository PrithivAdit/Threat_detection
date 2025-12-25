import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file")
    exit(1)

# Configure the API key
genai.configure(api_key=api_key)

# Create a model instance
model = genai.GenerativeModel('models/text-bison-001')

# Make a simple request
try:
    response = model.generate_content("Hello, world!")
    print("API Key is valid. Response:", response.text)
except Exception as e:
    print("ERROR: API Key validation failed:", str(e)) 