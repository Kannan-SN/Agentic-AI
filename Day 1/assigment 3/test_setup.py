"""
Test script to verify Financial Report Analyzer installation
"""

import sys
import os
from pathlib import Path

def test_python_packages():
    """Test if all required packages are installed"""
    print("🔍 Testing Python packages...")
    
    required_packages = [
        'PIL', 'cv2', 'openai', 'google.generativeai', 'pandas', 
        'numpy', 'requests', 'pytesseract', 'easyocr', 'matplotlib',
        'seaborn', 'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
                print(f"  ✅ Pillow (PIL): {PIL.__version__}")
            elif package == 'cv2':
                import cv2
                print(f"  ✅ OpenCV: {cv2.__version__}")
            elif package == 'google.generativeai':
                import google.generativeai as genai
                print(f"  ✅ Google AI: Available")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
                print(f"  ✅ {package}: {version}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}: Not installed")
    
    return len(missing_packages) == 0

def test_tesseract():
    """Test Tesseract OCR installation"""
    print("\n🔍 Testing Tesseract OCR...")
    
    try:
        import pytesseract
        
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"  ✅ Tesseract OCR: {version}")
        return True
    except Exception as e:
        print(f"  ❌ Tesseract OCR: {str(e)}")
        print("  💡 Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def test_api_keys():
    """Test API key configuration"""
    print("\n🔍 Testing API keys...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if openai_key and openai_key != 'your_openai_api_key_here':
        print(f"  ✅ OpenAI API Key: Configured ({openai_key[:10]}...)")
        return True
    elif google_key and google_key != 'your_google_api_key_here':
        print(f"  ✅ Google AI API Key: Configured ({google_key[:10]}...)")
        return True
    else:
        print("  ❌ No valid API keys found")
        print("  💡 Edit .env file and add your API key")
        return False

def test_project_structure():
    """Test project directory structure"""
    print("\n🔍 Testing project structure...")
    
    required_dirs = [
        'src', 'config', 'data/input_images', 'output/generated_reports'
    ]
    
    required_files = [
        'main.py', 'requirements.txt', '.env', 'src/image_processor.py',
        'src/ai_analyzer.py', 'src/report_generator.py'
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"  ✅ Directory: {directory}")
        else:
            print(f"  ❌ Directory missing: {directory}")
            all_good = False
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ File: {file}")
        else:
            print(f"  ❌ File missing: {file}")
            all_good = False
    
    return all_good

def test_sample_analysis():
    """Test with sample data"""
    print("\n🔍 Testing sample analysis...")
    
    try:
        # Import our modules
        sys.path.append('src')
        from report_generator import FinancialReportGenerator
        
        # Create sample data
        sample_data = {
            "executive_summary": "Test analysis completed successfully.",
            "key_metrics": {
                "revenue": {"value": "EUR 1.5B", "change": "+5%"}
            }
        }
        
        # Generate sample report
        generator = FinancialReportGenerator()
        report_file = generator.generate_comprehensive_report(sample_data, "Test Company")
        
        if Path(report_file).exists():
            print(f"  ✅ Sample report generated: {report_file}")
            return True
        else:
            print("  ❌ Failed to generate sample report")
            return False
    
    except Exception as e:
        print(f"  ❌ Sample analysis failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🤖 Financial Report Analyzer - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Python Packages", test_python_packages),
        ("Tesseract OCR", test_tesseract),
        ("API Keys", test_api_keys),
        ("Project Structure", test_project_structure),
        ("Sample Analysis", test_sample_analysis)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation is ready.")
        print("\n🚀 Next steps:")
        print("1. Place financial document images in data/input_images/")
        print("2. Run: python main.py --help")
        print("3. Try: python main.py path/to/image.png --company 'Company Name'")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        
        # Provide specific guidance
        if not results["API Keys"]:
            print("\n💡 To fix API Keys:")
            print("   - Edit .env file")
            print("   - Add your OpenAI or Google AI API key")
        
        if not results["Tesseract OCR"]:
            print("\n💡 To fix Tesseract:")
            print("   - Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   - Install and add to PATH")
        
        if not results["Python Packages"]:
            print("\n💡 To fix packages:")
            print("   - Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()