# namer_agent/config.py
# ==============================================================================
# ⚙️ Configration
# ==============================================================================
import os
from google.genai import types
from google.adk.models.google_llm import Gemini
import google.generativeai as genai

MODEL_NAME = "gemini-2.5-flash-lite"

# Configure standard retry logic for robustness
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503]
)

def get_model():
    """Returns the configured ADK Gemini model."""
    return Gemini(model=MODEL_NAME, retry_options=RETRY_CONFIG)

def configure_genai():
    """Configures the underlying GenAI SDK."""
    if "GOOGLE_API_KEY" in os.environ:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
