# Website Chatbot with Gemini AI

A Flask-based chatbot that can scrape websites and answer questions using Google's Gemini AI.

## Features

- Web scraping integration
- AI-powered responses using Gemini
- Chat history storage (MongoDB or in-memory)
- Session management
- Responsive web interface

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   export SECRET_KEY="your-secret-key"
   export MONGO_URI="mongodb://localhost:27017/"  # optional
   ```

3. Run the app:
   ```bash
   python app.py
   ```

## Deployment to Render

### 1. Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it (e.g., `website-chatbot`)
4. Don't initialize with README
5. Click "Create repository"

### 2. Upload Files to GitHub

**Option A: Git Commands (if Git installed)**
```bash
cd "c:\Users\vakam\OneDrive\Desktop\website chatbot"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

**Option B: Manual Upload**
1. Go to your GitHub repository
2. Click "Add file" → "Upload files"
3. Upload all files from your project folder:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `pyproject.toml`
   - `render.yaml`
   - `templates/index.html`
   - `scratch/` folder (optional)

### 3. Deploy on Render

1. Go to [Render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure settings:
   - **Name**: website-chatbot
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Python Version**: 3.11.0

5. Add Environment Variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `SECRET_KEY`: Any random string
   - `MONGO_URI`: Your MongoDB connection string (optional)

6. Click "Create Web Service"

## Environment Variables

- `GEMINI_API_KEY`: Required - Your Google Gemini API key
- `SECRET_KEY`: Optional - Flask session secret (auto-generated if not set)
- `MONGO_URI`: Optional - MongoDB connection string (falls back to in-memory storage)
- `FLASK_DEBUG`: Optional - Set to "true" for debug mode

## API Endpoints

- `GET /`: Main chat interface
- `POST /send_message`: Send a message to the chatbot
- `GET /get_history`: Get chat history for current session
- `POST /contact`: Contact form handler

## Technologies Used

- Flask (web framework)
- Google Gemini AI (AI responses)
- BeautifulSoup (web scraping)
- MongoDB (optional data storage)
- Gunicorn (production server)