# AI-Powered Financial Report Analyzer

## 📋 Requirements

- Python 3.8 or higher
- OpenAI API key (for GPT-4 Vision) or Google AI API key (for Gemini)
- Required Python packages (see requirements.txt)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd financial_report_analyzer
```

### 2. Create Virtual Environment
```bash
python -m venv venv
 On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
cp .env.template .env
# Edit .env file and add your API keys
```

### 5. Install Additional Dependencies

#### For Windows (Tesseract OCR):
- Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your system PATH

#### For Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## 🚀 Quick Start

### Basic Usage
```bash
# Analyze a single financial document
python main.py path/to/financial_report.png --company "ABN AMRO Bank"

# Analyze multiple images with custom output formats
python main.py image1.png image2.png --company "Company Name" --formats markdown json excel dashboard

# Extract specific metrics
python main.py balance_sheet.png --metrics ROE EPS Revenue CET1
```

### Programmatic Usage
```python
from src.image_processor import ImageProcessor
from src.ai_analyzer import FinancialAIAnalyzer
from src.report_generator import FinancialReportGenerator

# Initialize components
processor = ImageProcessor()
analyzer = FinancialAIAnalyzer(api_key="your-key", provider="openai")
generator = FinancialReportGenerator()

# Process images
images = processor.load_images(["path/to/financial_doc.png"])

# Analyze with AI
analysis = analyzer.analyze_financial_documents(images)

# Generate reports
reports = generator.generate_all_formats(analysis, "Company Name")
```

## 📊 Example Analysis Output

The system generates comprehensive analysis including:

### Key Financial Metrics
- **Net Profit**: EUR 690 million (-9.1% YoY)
- **Earnings Per Share**: EUR 0.78 (-8.2%)
- **Return on Equity**: 11.6% (Target: 9-10%)

### Financial Ratios
- **Cost/Income Ratio**: 59.2% (Target: 60%)
- **CET1 Ratio**: 14.1% (Basel III compliant)
- **Leverage Ratio**: 5.5% (Requirement: 3%)

### Risk Assessment
- Credit quality indicators
- Regulatory compliance status
- Key risk factors

## 🏗️ Project Structure

```
financial_report_analyzer/
├── src/                          # Source code
│   ├── image_processor.py        # Image loading and preprocessing
│   ├── ai_analyzer.py           # AI-powered analysis
│   ├── report_generator.py      # Report generation
│   └── utils.py                 # Utility functions
├── config/                      # Configuration files
│   └── config.py               # Application settings
├── data/                       # Input data
│   ├── input_images/           # Sample images
│   └── sample_reports/         # Sample reports
├── output/                     # Generated outputs
│   ├── processed_images/       # Processed images
│   └── generated_reports/      # Analysis reports
├── main.py                     # Main application
├── requirements.txt            # Python dependencies
├── .env.template              # Environment variables template
└── README.md                  # This file
```

## ⚙️ Configuration

Edit `config/config.py` to customize:

- **Image Processing**: Maximum image size, supported formats
- **AI Settings**: Model selection, temperature, max tokens
- **Output Settings**: Default formats, file naming
- **Analysis Prompts**: Custom prompts for different analysis types

## 🤖 Supported AI Providers

### OpenAI GPT-4 Vision
- Most comprehensive analysis
- Excellent chart/graph interpretation
- Higher accuracy for complex documents

### Google Gemini Pro Vision
- Fast processing
- Good multilingual support
- Cost-effective option

## 📈 Supported Financial Documents

- **Annual Reports**: Complete financial statements
- **Quarterly Reports**: Interim financial results
- **Balance Sheets**: Asset, liability, and equity statements
- **Income Statements**: Revenue and expense reports
- **Cash Flow Statements**: Operating, investing, financing activities
- **Financial Dashboards**: Visual performance metrics

## 🔧 Advanced Features

### Custom Analysis Prompts
```python
custom_prompt = """
Analyze this bank's quarterly report focusing on:
1. Credit risk indicators
2. Interest rate sensitivity
3. Capital adequacy trends
4. Digital transformation progress
"""

analysis = analyzer.analyze_financial_documents(images, custom_prompt)
```

### Specific Metric Extraction
```python
# Extract only specific metrics
metrics = analyzer.extract_specific_metrics(images, ['ROE', 'NIM', 'CET1'])
```

### Comparative Analysis
```python
# Compare with historical data
comparison = analyzer.generate_comparative_analysis(current_analysis, historical_data)
```

## 📊 Output Formats

### 1. Markdown Report
- Comprehensive analysis report
- Executive summary
- Key metrics tables
- Recommendations

### 2. JSON Data
- Structured data format
- API-friendly output
- Easy integration with other systems

### 3. Excel Spreadsheet
- Multiple worksheets for different sections
- Financial data tables
- Ratio calculations

### 4. Visual Dashboard
- Key metrics visualization
- Performance trends
- Risk assessment charts
