"""
AI Analysis Module for Financial Reports
Uses OpenAI GPT-4 Vision or Google Gemini for intelligent analysis
"""

import openai
import google.generativeai as genai
from PIL import Image
import json
from typing import List, Dict, Any
import base64
from io import BytesIO

class FinancialAIAnalyzer:
    def __init__(self, api_key: str, provider: str = "openai"):
        """
        Initialize AI analyzer
        
        Args:
            api_key: API key for the chosen provider
            provider: 'openai' or 'google'
        """
        self.provider = provider
        
        if provider == "openai":
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
        elif provider == "google":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
        
    def analyze_financial_documents(self, images: List[Image.Image], 
                                  user_prompt: str = None) -> Dict[str, Any]:
        """
        Analyze financial document images using AI
        
        Args:
            images: List of PIL Images
            user_prompt: Custom analysis prompt
            
        Returns:
            Dictionary containing analysis results
        """
        
        # Default comprehensive financial analysis prompt
        default_prompt = """
        Analyze these financial document images and provide a comprehensive analysis.
        
        Please extract and analyze:
        
        1. **Key Financial Metrics:**
           - Revenue/Net Interest Income
           - Net Profit/Income
           - Earnings Per Share (EPS)
           - Return on Equity (ROE)
           - Cost/Income Ratio
           
        2. **Balance Sheet Analysis:**
           - Total Assets
           - Total Liabilities
           - Shareholders' Equity
           - Loans and Advances
           - Deposits
           
        3. **Financial Ratios:**
           - Capital Adequacy Ratios (CET1, Basel III/IV)
           - Liquidity Ratios
           - Leverage Ratios
           - Cost of Risk
           
        4. **Performance Trends:**
           - Quarter-over-quarter changes
           - Year-over-year comparisons
           - Growth trends
           
        5. **Charts and Graphs Analysis:**
           - Interpret any visual data representations
           - Identify trends from graphical elements
           - Extract numerical data from charts
           
        6. **Risk Assessment:**
           - Credit quality indicators
           - Risk factors mentioned
           - Regulatory compliance status
           
        Provide the analysis in this JSON structure:
        {
            "executive_summary": "Brief overview of financial health",
            "key_metrics": {
                "revenue": {"value": "", "change": "", "period": ""},
                "net_income": {"value": "", "change": "", "period": ""},
                "eps": {"value": "", "change": "", "period": ""},
                "roe": {"value": "", "target": "", "status": ""}
            },
            "balance_sheet": {
                "total_assets": {"value": "", "change": ""},
                "total_liabilities": {"value": "", "change": ""},
                "equity": {"value": "", "change": ""}
            },
            "financial_ratios": {
                "cost_income_ratio": {"value": "", "target": ""},
                "cet1_ratio": {"value": "", "requirement": ""},
                "leverage_ratio": {"value": "", "requirement": ""}
            },
            "trends_analysis": [],
            "risk_assessment": {
                "credit_quality": "",
                "regulatory_status": "",
                "key_risks": []
            },
            "recommendations": []
        }
        """
        
        prompt = user_prompt if user_prompt else default_prompt
        
        if self.provider == "openai":
            return self._analyze_with_openai(images, prompt)
        elif self.provider == "google":
            return self._analyze_with_google(images, prompt)
    
    def _analyze_with_openai(self, images: List[Image.Image], prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI GPT-4 Vision"""
        try:
            # Prepare images for OpenAI API
            image_messages = []
            
            for img in images:
                # Convert to base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                image_messages.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_str}",
                        "detail": "high"
                    }
                })
            
            # Create the message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ] + image_messages
                }
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=4000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(result_text)
            except:
                return {"analysis": result_text}
                
        except Exception as e:
            return {"error": f"OpenAI analysis failed: {str(e)}"}
    
    def _analyze_with_google(self, images: List[Image.Image], prompt: str) -> Dict[str, Any]:
        """Analyze using Google Gemini Vision"""
        try:
            # Prepare content for Gemini
            content = [prompt] + images
            
            # Generate response
            response = self.model.generate_content(content)
            result_text = response.text
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(result_text)
            except:
                return {"analysis": result_text}
                
        except Exception as e:
            return {"error": f"Google analysis failed: {str(e)}"}
    
    def generate_comparative_analysis(self, current_analysis: Dict, 
                                    historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Generate comparative analysis with historical data
        """
        comparison_prompt = f"""
        Based on the current financial analysis and historical data, provide:
        
        1. Trend Analysis (3-5 quarters/years)
        2. Performance benchmarking
        3. Growth trajectory assessment
        4. Risk evolution analysis
        5. Strategic recommendations
        
        Current Analysis: {json.dumps(current_analysis, indent=2)}
        Historical Data: {json.dumps(historical_data, indent=2)}
        
        Provide insights on:
        - What's improving/deteriorating
        - Key performance drivers
        - Future outlook
        - Actionable recommendations
        """
        
        # This would typically use the same AI model for comparative analysis
        # For now, return a structured template
        return {
            "trend_analysis": "Analysis based on historical comparison",
            "performance_benchmarks": {},
            "strategic_recommendations": [],
            "outlook": "Future performance expectations"
        }
    
    def extract_specific_metrics(self, images: List[Image.Image], 
                               metrics_list: List[str]) -> Dict[str, Any]:
        """
        Extract specific financial metrics from images
        
        Args:
            images: List of financial document images
            metrics_list: Specific metrics to extract (e.g., ['ROE', 'EPS', 'Revenue'])
        """
        
        metrics_prompt = f"""
        From these financial document images, please extract the following specific metrics:
        
        Metrics to find: {', '.join(metrics_list)}
        
        For each metric, provide:
        - Current value
        - Previous period value (if available)
        - Percentage change
        - Time period
        - Any targets or benchmarks mentioned
        
        Return as JSON with metric names as keys.
        """
        
        if self.provider == "openai":
            return self._analyze_with_openai(images, metrics_prompt)
        elif self.provider == "google":
            return self._analyze_with_google(images, metrics_prompt)

# Example usage
if __name__ == "__main__":
    # Example with dummy API key - replace with actual key
    analyzer = FinancialAIAnalyzer("your-api-key-here", provider="openai")
    
    # Test with sample images
    from image_processor import ImageProcessor
    
    processor = ImageProcessor()
    images = processor.load_images(["sample_balance_sheet.png"])
    
    if images:
        analysis = analyzer.analyze_financial_documents(images)
        print(json.dumps(analysis, indent=2))