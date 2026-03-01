import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    print("Warning: MISTRAL_API_KEY not set. Please set it in .env")

# Model Definitions
REASONING_MODEL = "mistral-large-latest" # Simulating Magistral (Mistral Large is their current flagship reasoning model)
CODE_MODEL = "codestral-latest" # Simulating Devstral 2 (Codestral is the code model)
VISION_MODEL = "pixtral-large-latest" # For Grafana dashboards
VOICE_MODEL = "pixtral-12b-2409" # Placeholder for Voxtral Realtime (Voice API expected later, using a fast model for text-to-speech mock)
