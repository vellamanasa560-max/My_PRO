import os
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyA8Da8WXFm_pqm2Zgd-3AlGn7RN5FSEi-o"
genai.configure(api_key=GEMINI_API_KEY)

models_to_try = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro',
    'gemini-flash-latest',
    'gemini-3-flash-preview'
]

def test_models():
    for model_name in models_to_try:
        try:
            print(f"Testing model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            print(f"Success with {model_name}! Response: {response.text}")
            return model_name
        except Exception as e:
            print(f"Failed with {model_name}: {e}")
    return None

if __name__ == "__main__":
    test_models()
