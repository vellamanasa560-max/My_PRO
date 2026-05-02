import os
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyA8Da8WXFm_pqm2Zgd-3AlGn7RN5FSEi-o"
genai.configure(api_key=GEMINI_API_KEY)

def list_models():
    try:
        print("Listing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
