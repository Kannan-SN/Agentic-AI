"""
Main Application for Financial Report Analyzer
Integrates all modules to provide complete analysis workflow
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from image_processor import ImageProcessor
from ai_analyzer import FinancialAIAnalyzer
from report_generator import FinancialReportGenerator
from config.config import Config

class FinancialReportAnalyzer:
    def __init__(self, api_key: str = None, provider: str = "openai"):
        """
        Initialize the Financial Report Analyzer
        
        Args:
            api_key: API key for AI service
            provider: AI service provider ('openai' or 'google')
        """
        # Initialize components
        self.image_processor = ImageProcessor()
        
        # Use API key from config if not provided
        if not api_key:
            api_key = Config.OPENAI_API_KEY if provider == "openai" else Config.GOOGLE_API_KEY
        
        if not api_key:
            raise ValueError(f"No API key found for {provider}. Please set it in your .env file or pass it directly.")
        
        self.ai_analyzer = FinancialAIAnalyzer(api_key, provider)
        self.report_generator = FinancialReportGenerator()
        
        print(f"✅ Financial Report Analyzer initialized with {provider.upper()} AI")
    
    def analyze_financial_documents(self, 
                                  image_sources: List[str],
                                  company_name: str = "Company",
                                  custom_prompt: str = None,
                                  output_formats: List[str] = None) -> Dict[str, Any]:
        """
        Complete analysis workflow
        
        Args:
            image_sources: List of image file paths or URLs
            company_name: Name of the company being analyzed
            custom_prompt: Custom analysis prompt (optional)
            output_formats: List of output formats ['markdown', 'json', 'excel', 'dashboard']
            
        Returns:
            Dictionary containing analysis results and generated file paths
        """
        
        if output_formats is None:
            output_formats = ['markdown', 'json', 'dashboard']
        
        print(f"\n🔍 Starting analysis for {company_name}")
        print(f"📊 Processing {len(image_sources)} financial documents...")
        
        try:
            # Step 1: Load and preprocess images
            print("\n1️⃣ Loading and preprocessing images...")
            images = self.image_processor.load_images(image_sources)
            
            if not images:
                raise ValueError("No images could be loaded. Please check your file paths/URLs.")
            
            print(f"   ✅ Successfully loaded {len(images)} images")
            
            # Optional: Save processed images
            if Config.SAVE_PROCESSED_IMAGES:
                self.image_processor.save_processed_images(images, "output/processed_images")
            
            # Step 2: Extract text using OCR (for additional context)
            print("\n2️⃣ Extracting text content...")
            extracted_texts = []
            for i, img in enumerate(images):
                text = self.image_processor.extract_text_ocr(img)
                extracted_texts.append(text)
                print(f"   📄 Image {i+1}: {len(text)} characters extracted")
            
            # Step 3: Detect charts and tables
            print("\n3️⃣ Detecting charts and tables...")
            detected_regions = []
            for i, img in enumerate(images):
                regions = self.image_processor.detect_charts_and_tables(img)
                detected_regions.extend(regions)
                print(f"   📈 Image {i+1}: {len(regions)} regions detected")
            
            # Step 4: AI Analysis
            print("\n4️⃣ Performing AI analysis...")
            analysis_result = self.ai_analyzer.analyze_financial_documents(images, custom_prompt)
            
            if 'error' in analysis_result:
                print(f"   ❌ AI Analysis failed: {analysis_result['error']}")
                return {"error": analysis_result['error']}
            
            print("   ✅ AI analysis completed successfully")
            
            # Step 5: Enhance analysis with OCR data
            analysis_result['ocr_data'] = {
                'extracted_texts': extracted_texts,
                'detected_regions': detected_regions,
                'total_text_length': sum(len(text) for text in extracted_texts)
            }
            
            # Step 6: Generate reports
            print("\n5️⃣ Generating reports...")
            generated_files = {}
            
            if 'markdown' in output_formats:
                md_file = self.report_generator.generate_comprehensive_report(
                    analysis_result, company_name
                )
                generated_files['markdown'] = md_file
                print(f"   📝 Markdown report: {md_file}")
            
            if 'json' in output_formats:
                json_file = self.report_generator.generate_json_report(
                    analysis_result, company_name
                )
                generated_files['json'] = json_file
                print(f"   📋 JSON report: {json_file}")
            
            if 'excel' in output_formats:
                excel_file = self.report_generator.export_to_excel(
                    analysis_result, company_name
                )
                if excel_file:
                    generated_files['excel'] = excel_file
                    print(f"   📊 Excel report: {excel_file}")
            
            if 'dashboard' in output_formats:
                dashboard_file = self.report_generator.create_summary_dashboard(
                    analysis_result, company_name
                )
                generated_files['dashboard'] = dashboard_file
                print(f"   📈 Dashboard: {dashboard_file}")
            
            # Step 7: Summary
            print(f"\n✅ Analysis completed successfully!")
            print(f"🏢 Company: {company_name}")
            print(f"📁 Generated {len(generated_files)} report files")
            
            return {
                'analysis': analysis_result,
                'generated_files': generated_files,
                'summary': {
                    'company_name': company_name,
                    'images_processed': len(images),
                    'text_extracted': sum(len(text) for text in extracted_texts),
                    'regions_detected': len(detected_regions),
                    'reports_generated': len(generated_files)
                }
            }
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def analyze_specific_metrics(self, 
                               image_sources: List[str], 
                               metrics: List[str]) -> Dict[str, Any]:
        """
        Extract specific financial metrics from documents
        
        Args:
            image_sources: List of image file paths or URLs
            metrics: List of specific metrics to extract
        """
        
        print(f"\n🎯 Extracting specific metrics: {', '.join(metrics)}")
        
        try:
            images = self.image_processor.load_images(image_sources)
            if not images:
                raise ValueError("No images could be loaded.")
            
            result = self.ai_analyzer.extract_specific_metrics(images, metrics)
            
            print("✅ Specific metrics extraction completed")
            return result
            
        except Exception as e:
            error_msg = f"Specific metrics extraction failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

def main():
    """Command line interface for the Financial Report Analyzer"""
    
    parser = argparse.ArgumentParser(description="AI-Powered Financial Report Analyzer")
    parser.add_argument("images", nargs="+", help="Paths to financial document images or URLs")
    parser.add_argument("--company", "-c", default="Company", help="Company name")
    parser.add_argument("--provider", "-p", choices=['openai', 'google'], default='openai', 
                       help="AI service provider")
    parser.add_argument("--api-key", "-k", help="API key for AI service")
    parser.add_argument("--formats", "-f", nargs="+", 
                       choices=['markdown', 'json', 'excel', 'dashboard'],
                       default=['markdown', 'json', 'dashboard'],
                       help="Output formats to generate")
    parser.add_argument("--metrics", "-m", nargs="+", 
                       help="Specific metrics to extract (e.g., ROE EPS Revenue)")
    parser.add_argument("--prompt", help="Custom analysis prompt")
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = FinancialReportAnalyzer(
            api_key=args.api_key,
            provider=args.provider
        )
        
        if args.metrics:
            # Extract specific metrics
            result = analyzer.analyze_specific_metrics(args.images, args.metrics)
            print(f"\n📊 Extracted Metrics:")
            print(json.dumps(result, indent=2))
        else:
            # Full analysis
            result = analyzer.analyze_financial_documents(
                image_sources=args.images,
                company_name=args.company,
                custom_prompt=args.prompt,
                output_formats=args.formats
            )
            
            if 'error' not in result:
                print(f"\n📊 Analysis Summary:")
                print(f"   Company: {result['summary']['company_name']}")
                print(f"   Images processed: {result['summary']['images_processed']}")
                print(f"   Text extracted: {result['summary']['text_extracted']} characters")
                print(f"   Reports generated: {result['summary']['reports_generated']}")
                
                print(f"\n📁 Generated Files:")
                for format_type, filepath in result['generated_files'].items():
                    print(f"   {format_type.title()}: {filepath}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("🤖 Financial Report Analyzer")
        print("="*50)
        print("\n📋 Example Usage:")
        print("python main.py path/to/financial_report.png --company 'ABN AMRO Bank'")
        print("python main.py url1 url2 --company 'Company Name' --formats markdown json excel")
        print("python main.py image.png --metrics ROE EPS Revenue")
        print("\n💡 For help: python main.py --help")
        
        # Demo with sample data
        print("\n🧪 Running demo with sample analysis...")
        
        sample_analysis = {
            "executive_summary": "Demo analysis of financial documents showing strong performance indicators.",
            "key_metrics": {
                "revenue": {"value": "EUR 1,638M", "change": "+7% YoY", "period": "Q3 2024"},
                "net_income": {"value": "EUR 690M", "change": "-9.1% YoY", "period": "Q3 2024"},
                "eps": {"value": "EUR 0.78", "change": "-8.2%", "period": "Q3 2024"}
            },
            "financial_ratios": {
                "cost_income_ratio": {"value": "59.2%", "target": "60%"},
                "cet1_ratio": {"value": "14.1%", "requirement": "Basel III"}
            }
        }
        
        # Generate demo report
        generator = FinancialReportGenerator()
        demo_files = generator.generate_all_formats(sample_analysis, "Demo Company")
        
        print("\n📁 Demo reports generated:")
        for format_type, filepath in demo_files.items():
            print(f"   {format_type.title()}: {filepath}")
    else:
        main()