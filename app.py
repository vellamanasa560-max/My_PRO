import os
import requests
from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime
import google.generativeai as genai
from bs4 import BeautifulSoup
import re
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# Gemini Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# MongoDB Configuration with Fallback
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
use_mongo = True
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client['chatbot_db']
    messages_col = db['messages']
    website_context_col = db['website_context']
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"MongoDB not available, using in-memory storage.")
    use_mongo = False
    memory_messages = []
    memory_context = {}

def scrape_website(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text[:5000]
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

def extract_url(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    match = url_pattern.search(text)
    return match.group(0) if match else None

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = 'guest_' + os.urandom(4).hex()
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        user_id = session.get('user_id', 'guest')
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"success": False, "message": "Empty message"}), 400

        url = extract_url(user_message)
        context = ""
        
        if url:
            scraped_content = scrape_website(url)
            if scraped_content:
                if use_mongo:
                    website_context_col.update_one(
                        {"user_id": user_id},
                        {"$set": {"url": url, "content": scraped_content, "timestamp": datetime.utcnow()}},
                        upsert=True
                    )
                else:
                    memory_context[user_id] = {"url": url, "content": scraped_content}
                context = f"\n\nContext from website ({url}):\n{scraped_content}"
            else:
                return jsonify({"success": True, "reply": "I couldn't reach that website. Please check the URL."})

        if not url:
            if use_mongo:
                existing_context = website_context_col.find_one({"user_id": user_id})
                if existing_context:
                    context = f"\n\nContext from previously provided website ({existing_context['url']}):\n{existing_context['content']}"
            else:
                existing_context = memory_context.get(user_id)
                if existing_context:
                    context = f"\n\nContext from previously provided website ({existing_context['url']}):\n{existing_context['content']}"

        prompt = f"You are ChatNexus, a premium AI assistant. Answer using the provided website context if available. {context}\n\nUser: {user_message}\nAssistant:"

        try:
            response = model.generate_content(prompt)
            bot_reply = response.text
        except Exception as e:
            bot_reply = "I'm experiencing a brief connection issue. Please try again in a moment."

        msg_data = {"user_id": user_id, "sender": "user", "text": user_message, "timestamp": datetime.utcnow()}
        bot_data = {"user_id": user_id, "sender": "bot", "text": bot_reply, "timestamp": datetime.utcnow()}

        if use_mongo:
            messages_col.insert_one(msg_data)
            messages_col.insert_one(bot_data)
        else:
            memory_messages.append(msg_data)
            memory_messages.append(bot_data)

        return jsonify({"success": True, "reply": bot_reply})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    user_id = session.get('user_id', 'guest')
    if use_mongo:
        history = list(messages_col.find({"user_id": user_id}).sort("timestamp", 1))
        for msg in history:
            msg['_id'] = str(msg['_id'])
    else:
        history = [m for m in memory_messages if m['user_id'] == user_id]
    return jsonify({"success": True, "history": history})

@app.route('/contact', methods=['POST'])
def contact():
    # Simulate contact form processing
    return jsonify({"success": True, "message": "Thank you for your message! Our team will contact you soon."})

if __name__ == '__main__':
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
