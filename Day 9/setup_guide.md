# Quick Setup Guide

## Prerequisites
- Python 3.10 or higher
- MongoDB (local or cloud)
- Google AI API key

## Step-by-Step Setup

### 1. Install Dependencies
```bash
# Try the requirements file first
pip install -r requirements.txt

# If that fails, install core packages individually:
pip install streamlit pymongo python-dotenv pandas numpy plotly
pip install google-generativeai
pip install langchain langchain-google-genai
pip install chromadb sentence-transformers
pip install beautifulsoup4 requests aiohttp pydantic

# Install AI frameworks (may need different versions)
pip install crewai
pip install langgraph
pip install autogen-agentchat

# Check what was installed
python main.py --check
```

### 2. Setup Environment
```bash
# Copy the example environment file
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux

# Edit .env and add your API key:
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Start MongoDB
Choose one option:

**Option A: Local MongoDB**
```bash
mongod
```

**Option B: Docker**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option C: MongoDB Atlas (Cloud)**
- Update MONGODB_URI in .env with your Atlas connection string

### 4. Run the Application
```bash
python main.py
```

The application will start at: http://localhost:8501

## Troubleshooting

### Common Issues

**1. Package Installation Errors**
- Use Python 3.10+ (check: `python --version`)
- Try installing packages one by one
- Use `pip install --upgrade pip` first

**2. Google API Key Issues**
- Get key from: https://aistudio.google.com/app/apikey
- Make sure it's added to .env file correctly
- No quotes needed: `GOOGLE_API_KEY=your_key_here`

**3. MongoDB Connection Issues**
- Check if MongoDB is running: `mongod`
- Try different port in .env: `MONGODB_URI=mongodb://localhost:27017/`
- For Windows: Install MongoDB Community Server

**4. Port Already in Use**
- Change port in main.py: `--server.port=8502`
- Or kill existing process: `pkill -f streamlit`

### Minimal Setup (If Some Packages Fail)

You can run with minimal packages:
```bash
pip install streamlit pymongo google-generativeai python-dotenv pandas plotly
```

The system will work with basic functionality and can be enhanced later.

## Getting Your Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the generated key
5. Add it to your .env file

## Testing the Setup

1. Run `python main.py --check` to verify dependencies
2. Start the application with `python main.py`
3. Open http://localhost:8501 in your browser
4. Try creating a student profile
5. Mine some alumni data
6. Generate referral recommendations
