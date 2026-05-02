import os
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient

# GEMINI_API_KEY = "AIzaSyA8Da8WXFm_pqm2Zgd-3AlGn7RN5FSEi-o"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyA8Da8WXFm_pqm2Zgd-3AlGn7RN5FSEi-o")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def test_gemini():
    try:
        print("Testing Gemini API...")
        response = model.generate_content("Hello, how are you?")
        print(f"Gemini Response: {response.text}")
        return True
    except Exception as e:
        print(f"Gemini Error: {e}")
        return False

def test_mongodb():
    try:
        print("Testing MongoDB connection...")
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info() # Trigger connection
        print("MongoDB Connection Successful!")
        return True
    except Exception as e:
        print(f"MongoDB Error: {e}")
        return False

if __name__ == "__main__":
    gemini_ok = test_gemini()
    mongo_ok = test_mongodb()
    
    if gemini_ok and mongo_ok:
        print("\nAll systems GO!")
    else:
        print("\nSome systems failed. Check errors above.")
