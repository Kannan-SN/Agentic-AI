"""
Package installer script for Financial Report Analyzer
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("📦 Installing Financial Report Analyzer Dependencies")
    print("=" * 60)
    
    # Upgrade pip first
    print("🔄 Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # List of required packages
    packages = [
        "Pillow==10.0.1",
        "opencv-python==4.8.1.78", 
        "openai==1.3.7",
        "google-generativeai==0.3.2",
        "pandas==2.1.3",
        "numpy==1.25.2",
        "requests==2.31.0",
        "urllib3==2.1.0",
        "pytesseract==0.3.10",
        "easyocr==1.7.0",
        "matplotlib==3.8.2",
        "seaborn==0.13.0",
        "python-dotenv==1.0.0",
        "openpyxl"
    ]
    
    print(f"\n📋 Installing {len(packages)} packages...")
    
    failed_packages = []
    
    for package in packages:
        print(f"\n🔄 Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 60)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 60)
    
    successful = len(packages) - len(failed_packages)
    print(f"✅ Successfully installed: {successful}/{len(packages)} packages")
    
    if failed_packages:
        print(f"❌ Failed packages: {len(failed_packages)}")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        print("\n💡 Try installing failed packages manually:")
        for pkg in failed_packages:
            print(f"   pip install {pkg}")
    else:
        print("🎉 All packages installed successfully!")
        print("\n🚀 Next steps:")
        print("1. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Add your API key to .env file")
        print("3. Run: python test_setup.py")

if __name__ == "__main__":
    main()