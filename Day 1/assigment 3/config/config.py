"""
Configuration file for Financial Report Analyzer
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys (set these in your .env file)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Image processing settings
    MAX_IMAGE_SIZE = (1024, 1024)
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # Analysis settings
    DEFAULT_MODEL = 'gpt-4-vision-preview'
    MAX_TOKENS = 4000
    TEMPERATURE = 0.1
    
    # Output settings
    OUTPUT_FORMAT = 'json'
    SAVE_PROCESSED_IMAGES = True
    
    # Prompts
    FINANCIAL_ANALYSIS_PROMPT = """
    You are a expert financial analyst. Analyze the provided financial document image and extract key information.
    
    Focus on:
    1. Key Financial Metrics (Revenue, Net Income, EPS, etc.)
    2. Financial Ratios (ROE, Cost/Income, CET1, etc.)
    3. Balance Sheet items (Assets, Liabilities, Equity)
    4. Trends and comparisons with previous periods
    5. Charts and graphs analysis
    6. Risk factors and outlook
    
    Provide a structured summary with:
    - Executive Summary
    - Key Performance Indicators
    - Financial Health Assessment
    - Notable Trends
    - Risk Analysis
    - Recommendations
    """