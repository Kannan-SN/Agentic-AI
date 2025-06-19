import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    
    project_root = Path(__file__).parent.parent
    
    config = {
        # API Keys
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        
        # Database
        "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME", "alumni_network"),
        
        # LinkedIn (for scraping)
        "LINKEDIN_EMAIL": os.getenv("LINKEDIN_EMAIL"),
        "LINKEDIN_PASSWORD": os.getenv("LINKEDIN_PASSWORD"),
        
        # Logging
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        
        # Project paths
        "PROJECT_ROOT": project_root,
        "DATA_DIR": project_root / "data",
        "LOGS_DIR": project_root / "logs",
        
        # Model configurations
        "GEMINI_MODEL": "gemini-1.5-flash",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
        "VECTOR_STORE_PATH": project_root / "data" / "vector_store",
        
        # Agent configurations
        "MAX_ITERATIONS": 5,
        "TEMPERATURE": 0.7,
        "MAX_TOKENS": 4000,
        
        # UI configurations
        "STREAMLIT_PORT": 8501,
        "PAGE_TITLE": "Alumni Referrer Network Builder",
    }
    
    # Create necessary directories
    config["DATA_DIR"].mkdir(exist_ok=True)
    config["LOGS_DIR"].mkdir(exist_ok=True)
    config["VECTOR_STORE_PATH"].mkdir(exist_ok=True)
    
    return config

# Validate required environment variables
def validate_config(config: Dict[str, Any]) -> bool:
    """Validate that required configuration is present"""
    required_keys = ["GOOGLE_API_KEY"]
    
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        print(f"❌ Missing required configuration: {', '.join(missing_keys)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    
    return True