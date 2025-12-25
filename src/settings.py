import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-flash"
TOKEN_LIMIT = 12000  # Free tier safety limit
FRAMES_PER_PROMPT = 10  # Sample every 10th frame
MAX_TOKENS = 500
