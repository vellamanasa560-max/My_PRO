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
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# =========================
# Gemini Configuration
# =========================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("WARNING: GEMINI_API_KEY not set. AI responses disabled.")
    model = None

# =========================
# MongoDB Configuration
# =========================
MONGO_URI = os.environ.get("MONGO_URI")

use_mongo = False
memory_messages = []
memory_context = {}

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client['chatbot_db']
        messages_col = db['messages']
        website_context_col = db['website_context']
        use_mongo = True
        print("Connected to MongoDB.")
    except Exception as e:
        print("MongoDB connection failed, using memory.")

# =========================
# Helpers
# =========================
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
        print("Scraping error:", e)
        return None


def extract_url(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    match = url_pattern.search(text)
    return match.group(0) if match else None


# =========================
# Routes
# =========================
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

        # -------------------------
        # Handle URL scraping
        # -------------------------
        if url:
            scraped_content = scrape_website(url)

            if scraped_content:
                if use_mongo:
                    website_context_col.update_one(
                        {"user_id": user_id},
                        {"$set": {
                            "url": url,
                            "content": scraped_content,
                            "timestamp": datetime.utcnow()
                        }},
                        upsert=True
                    )
                else:
                    memory_context[user_id] = {
                        "url": url,
                        "content": scraped_content
                    }

                context = f"\n\nContext from {url}:\n{scraped_content}"
            else:
                return jsonify({
                    "success": True,
                    "reply": "Couldn't access that website."
                })

        else:
            if use_mongo:
                existing = website_context_col.find_one({"user_id": user_id})
            else:
                existing = memory_context.get(user_id)

            if existing:
                context = f"\n\nContext from {existing['url']}:\n{existing['content']}"

        # -------------------------
        # AI Response
        # -------------------------
        prompt = f"""
You are ChatNexus AI.
Use website context if available.

{context}

User: {user_message}
Assistant:
"""

        if model:
            try:
                response = model.generate_content(prompt)
                bot_reply = response.text
            except Exception as e:
                print("Gemini error:", e)
                bot_reply = "AI error. Try again later."
        else:
            bot_reply = "AI is not configured."

        # -------------------------
        # Store Messages
        # -------------------------
        msg_user = {
            "user_id": user_id,
            "sender": "user",
            "text": user_message,
            "timestamp": datetime.utcnow()
        }

        msg_bot = {
            "user_id": user_id,
            "sender": "bot",
            "text": bot_reply,
            "timestamp": datetime.utcnow()
        }

        if use_mongo:
            messages_col.insert_one(msg_user)
            messages_col.insert_one(msg_bot)
        else:
            memory_messages.append(msg_user)
            memory_messages.append(msg_bot)

        return jsonify({"success": True, "reply": bot_reply})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/get_history')
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
    return jsonify({
        "success": True,
        "message": "We’ll contact you soon."
    })


# =========================
# Run (local only)
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
