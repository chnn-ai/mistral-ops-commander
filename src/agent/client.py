from mistralai import Mistral
from src.config import MISTRAL_API_KEY

def get_mistral_client() -> Mistral:
    """Returns an authenticated Mistral SDK client."""
    return Mistral(api_key=MISTRAL_API_KEY)
