#!/usr/bin/env python3
"""
Alumni Referrer Network Builder - Main Entry Point
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_packages = []
    
    try:
        import streamlit
    except ImportError:
        missing_packages.append("streamlit")
    
    try:
        import pymongo
    except ImportError:
        missing_packages.append("pymongo")
    
    try:
        import google.generativeai
    except ImportError:
        missing_packages.append("google-generativeai")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages:")
        print("pip install " + " ".join(missing_packages))
        return False
    
    return True

def initialize_project():
    """Initialize the project with necessary configurations"""
    print("🚀 Initializing Alumni Referrer Network Builder...")
    
    # Check dependencies first
    if not check_dependencies():
        return False
    
    try:
        from config.settings import load_config, validate_config
        from utils.logger import setup_logging
        from database.mongodb_client import MongoDBClient
        
        # Load configuration
        config = load_config()
        
        # Validate configuration
        if not validate_config(config):
            print("❌ Configuration validation failed. Please check your .env file.")
            print("Make sure you have:")
            print("1. Created .env file from .env.example")
            print("2. Added your Google API key")
            print("3. Set MongoDB URI (or use default)")
            return False
        
        # Setup logging
        logger = setup_logging()
        logger.info("Starting Alumni Referrer Network Builder")
        
        # Initialize database
        try:
            db_client = MongoDBClient()
            db_client.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            print("❌ Database connection failed. Please check your MongoDB setup.")
            print("Options:")
            print("1. Install and start MongoDB locally: mongod")
            print("2. Use Docker: docker run -d -p 27017:27017 mongo")
            print("3. Update MONGODB_URI in .env for cloud MongoDB")
            return False
        
        print("✅ Project initialized successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required packages are installed:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    try:
        print("🌐 Starting Streamlit UI...")
        print("📱 Open your browser and go to: http://localhost:8501")
        
        streamlit_path = project_root / "ui" / "streamlit_app.py"
        
        # Check if streamlit_app.py exists
        if not streamlit_path.exists():
            print(f"❌ Streamlit app not found at: {streamlit_path}")
            return False
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_path), 
            "--server.port=8501",
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Alumni Network Builder stopped by user")
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        print("Try running manually:")
        print(f"streamlit run {streamlit_path}")

def show_help():
    """Show help information"""
    print("""
🎓 Alumni Referrer Network Builder
=====================================

Setup Instructions:
1. Install Python 3.10+
2. Install requirements: pip install -r requirements.txt
3. Copy .env.example to .env
4. Add your Google API key to .env
5. Start MongoDB (mongod or Docker)
6. Run: python main.py

Features:
- 🤖 Four AI Agents (CrewAI, LangChain, LangGraph, AutoGen)
- 🔍 RAG Implementation with ChromaDB
- 🎯 Intelligent Alumni-Student Matching
- 📧 Automated Message Generation
- 📊 Interactive Analytics Dashboard

For support: Check README.md or create an issue on GitHub
""")

if __name__ == "__main__":
    print("🎓 Alumni Referrer Network Builder")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h", "help"]:
            show_help()
            sys.exit(0)
        elif sys.argv[1] == "--check":
            print("🔍 Checking dependencies...")
            if check_dependencies():
                print("✅ All dependencies are installed!")
            sys.exit(0)
    
    # Initialize and run
    if initialize_project():
        run_streamlit_app()
    else:
        print("\n❌ Project initialization failed.")
        print("Run 'python main.py --help' for setup instructions.")
        sys.exit(1)#!/usr/bin/env python3
"""
Alumni Referrer Network Builder - Main Entry Point
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import load_config
from utils.logger import setup_logging
from database.mongodb_client import MongoDBClient

def initialize_project():
    """Initialize the project with necessary configurations"""
    print("🚀 Initializing Alumni Referrer Network Builder...")
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Alumni Referrer Network Builder")
    
    # Initialize database
    try:
        db_client = MongoDBClient()
        db_client.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        print("❌ Database connection failed. Please check your MongoDB setup.")
        return False
    
    print("✅ Project initialized successfully!")
    return True

def run_streamlit_app():
    """Run the Streamlit application"""
    try:
        print("🌐 Starting Streamlit UI...")
        streamlit_path = project_root / "ui" / "streamlit_app_fixed.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_path), 
            "--server.port=8501",
            "--server.headless=true"
        ])
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

if __name__ == "__main__":
    if initialize_project():
        run_streamlit_app()
    else:
        print("❌ Project initialization failed. Please check the configuration.")
        sys.exit(1)