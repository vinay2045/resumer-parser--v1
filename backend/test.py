import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Debug check (IMPORTANT)
print("API KEY LOADED:", bool(os.getenv("GEMINI_API_KEY")))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = genai.list_models()

for m in models:
    print("\nMODEL:", m.name)
    print("SUPPORTED:", m.supported_generation_methods)
