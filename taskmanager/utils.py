# taskmanager/utils.py
import google.generativeai as genai
from django.conf import settings

# Configure Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_roadmap(prompt: str) -> str:
    """
    Generate a task roadmap using Gemini AI.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text
