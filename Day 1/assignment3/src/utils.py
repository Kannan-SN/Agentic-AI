"""
Utility functions for Financial Report Analyzer
"""

import re
import json
from typing import Dict, Any, List, Union
import pandas as pd
from pathlib import Path
import logging

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('financial_analyzer.log'),
            logging.StreamHandler()
        ]
    )

def extract_financial_numbers(text: str) -> Dict[str, List[str]]:
    """
    Extract financial numbers and currencies from text
    
    Args:
        text: Input text containing financial data
        
    Returns:
        Dictionary with extracted numbers categorized by type
    """
    patterns = {
        'currencies': r'(?:EUR|USD|GBP|JPY)\s*[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?',
        'percentages': r'\d+(?:\.\d+)?%',
        'ratios': r'\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?',
        'large_numbers': r'\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|thousand|M|B|K))?'
    }
    
    extracted = {}
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        extracted[pattern_name] = matches
    
    return extracted

def standardize_financial_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize financial metric names and formats
    
    Args:
        data: Raw financial data dictionary
        
    Returns:
        Standardized data dictionary
    """
    
    metric_mappings = {
        'net_profit': ['net profit', 'net income', 'profit after tax'],
        'revenue': ['total revenue', 'net revenue', 'sales', 'turnover'],
        'eps': ['earnings per share', 'eps', 'earning per share'],
        'roe': ['return on equity', 'roe', 'return on shareholders equity'],
        'roa': ['return on assets', 'roa'],
        'cost_income_ratio': ['cost income ratio', 'cost/income ratio', 'efficiency ratio'],
        'cet1_ratio': ['cet1 ratio', 'common equity tier 1 ratio', 'capital ratio'],
        'leverage_ratio': ['leverage ratio', 'tier 1 leverage ratio']
    }
    
    standardized = {}
    
    def find_standard_key(raw_key: str) -> str:
        raw_key_lower = raw_key.lower().strip()
        for standard_key, variations in metric_mappings.items():
            if raw_key_lower in variations or any(var in raw_key_lower for var in variations):
                return standard_key
        return raw_key.lower().replace(' ', '_').replace('/', '_')
    
    for key, value in data.items():
        if isinstance(key, str):
            standard_key = find_standard_key(key)
            standardized[standard_key] = value
        else:
            standardized[key] = value
    
    return standardized

def validate_financial_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate financial data for completeness and consistency
    
    Args:
        data: Financial data dictionary
        
    Returns:
        Dictionary with validation results
    """
    
    validation_results = {
        'missing_fields': [],
        'inconsistencies': [],
        'warnings': [],
        'errors': []
    }
    
    # Required fields for basic financial analysis
    required_fields = [
        'revenue', 'net_income', 'total_assets', 'total_liabilities'
    ]
    
    # Check for missing required fields
    for field in required_fields:
        if field not in data or not data[field]:
            validation_results['missing_fields'].append(field)
    
    # Check for data consistency
    if 'total_assets' in data and 'total_liabilities' in data and 'equity' in data:
        try:
            # Extract numerical values (simplified)
            assets_str = str(data['total_assets'])
            liabilities_str = str(data['total_liabilities'])
            equity_str = str(data['equity'])
            
            # This is a simplified check - in practice, you'd parse the actual numbers
            if len(assets_str) > 0 and len(liabilities_str) > 0 and len(equity_str) > 0:
                validation_results['warnings'].append("Balance sheet equation should be verified: Assets = Liabilities + Equity")
        except:
            validation_results['errors'].append("Could not validate balance sheet equation")
    
    # Check for reasonable ratios
    if 'roe' in data:
        roe_str = str(data['roe']).lower()
        if 'roe' in roe_str or '%' in roe_str:
            # Extract percentage if possible
            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', roe_str)
            if percentage_match:
                roe_value = float(percentage_match.group(1))
                if roe_value > 100:
                    validation_results['warnings'].append(f"ROE seems unusually high: {roe_value}%")
                elif roe_value < 0:
                    validation_results['warnings'].append(f"Negative ROE detected: {roe_value}%")
    
    return validation_results

def create_comparison_table(current_data: Dict[str, Any], 
                          historical_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a comparison table with current and historical data
    
    Args:
        current_data: Current period financial data
        historical_data: List of historical period data
        
    Returns:
        Pandas DataFrame with comparison data
    """
    
    # Extract common metrics
    all_metrics = set(current_data.keys())
    for hist_data in historical_data:
        all_metrics.update(hist_data.keys())
    
    # Create comparison table
    comparison_data = {}
    
    # Add current period
    comparison_data['Current'] = current_data
    
    # Add historical periods
    for i, hist_data in enumerate(historical_data):
        period_name = f"Period_{i+1}"
        comparison_data[period_name] = hist_data
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(comparison_data, orient='index')
    df = df.reindex(sorted(df.columns))  # Sort columns alphabetically
    
    return df

def calculate_growth_rates(current_value: str, previous_value: str) -> Dict[str, Union[float, str]]:
    """
    Calculate growth rates between current and previous values
    
    Args:
        current_value: Current period value as string
        previous_value: Previous period value as string
        
    Returns:
        Dictionary with growth calculations
    """
    
    def extract_number(value_str: str) -> float:
        """Extract numerical value from string"""
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^\d.-]', '', str(value_str))
        try:
            return float(cleaned)
        except:
            return None
    
    current_num = extract_number(current_value)
    previous_num = extract_number(previous_value)
    
    result = {
        'current_value': current_value,
        'previous_value': previous_value,
        'current_numeric': current_num,
        'previous_numeric': previous_num
    }
    
    if current_num is not None and previous_num is not None and previous_num != 0:
        growth_rate = ((current_num - previous_num) / previous_num) * 100
        result['growth_rate_percent'] = round(growth_rate, 2)
        result['growth_direction'] = 'increase' if growth_rate > 0 else 'decrease' if growth_rate < 0 else 'stable'
        result['absolute_change'] = current_num - previous_num
    else:
        result['growth_rate_percent'] = None
        result['growth_direction'] = 'unknown'
        result['absolute_change'] = None
        result['error'] = 'Could not calculate growth rate'
    
    return result

def format_currency(amount: Union[str, float], currency: str = "EUR") -> str:
    """
    Format numerical amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency code (EUR, USD, etc.)
        
    Returns:
        Formatted currency string
    """
    
    try:
        if isinstance(amount, str):
            # Extract number from string
            num_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)', amount.replace(',', ''))
            if num_match:
                amount = float(num_match.group(1))
            else:
                return str(amount)  # Return original if can't parse
        
        # Format based on size
        if amount >= 1_000_000_000:
            return f"{currency} {amount/1_000_000_000:.1f}B"
        elif amount >= 1_000_000:
            return f"{currency} {amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"{currency} {amount/1_000:.1f}K"
        else:
            return f"{currency} {amount:.2f}"
    
    except:
        return str(amount)

def export_analysis_summary(analysis_data: Dict[str, Any], 
                          output_file: str = "analysis_summary.txt") -> str:
    """
    Export a quick text summary of the analysis
    
    Args:
        analysis_data: Analysis results dictionary
        output_file: Output file path
        
    Returns:
        Path to generated summary file
    """
    
    summary_lines = []
    summary_lines.append("FINANCIAL ANALYSIS SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append("")
    
    # Executive Summary
    if 'executive_summary' in analysis_data:
        summary_lines.append("EXECUTIVE SUMMARY:")
        summary_lines.append(analysis_data['executive_summary'])
        summary_lines.append("")
    
    # Key Metrics
    if 'key_metrics' in analysis_data:
        summary_lines.append("KEY FINANCIAL METRICS:")
        summary_lines.append("-" * 25)
        for metric, data in analysis_data['key_metrics'].items():
            if isinstance(data, dict):
                metric_name = metric.replace('_', ' ').title()
                value = data.get('value', 'N/A')
                change = data.get('change', '')
                summary_lines.append(f"{metric_name}: {value} {change}")
        summary_lines.append("")
    
    # Financial Ratios
    if 'financial_ratios' in analysis_data:
        summary_lines.append("FINANCIAL RATIOS:")
        summary_lines.append("-" * 18)
        for ratio, data in analysis_data['financial_ratios'].items():
            if isinstance(data, dict):
                ratio_name = ratio.replace('_', ' ').title()
                value = data.get('value', 'N/A')
                target = data.get('target', data.get('requirement', ''))
                summary_lines.append(f"{ratio_name}: {value} (Target: {target})")
        summary_lines.append("")
    
    # Risk Assessment
    if 'risk_assessment' in analysis_data and 'key_risks' in analysis_data['risk_assessment']:
        summary_lines.append("KEY RISKS:")
        summary_lines.append("-" * 10)
        for risk in analysis_data['risk_assessment']['key_risks']:
            summary_lines.append(f"• {risk}")
        summary_lines.append("")
    
    # Recommendations
    if 'recommendations' in analysis_data:
        summary_lines.append("RECOMMENDATIONS:")
        summary_lines.append("-" * 15)
        for i, rec in enumerate(analysis_data['recommendations'], 1):
            summary_lines.append(f"{i}. {rec}")
    
    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    return str(output_path)

def parse_financial_statement_structure(text: str) -> Dict[str, List[str]]:
    """
    Parse and categorize financial statement sections from OCR text
    
    Args:
        text: OCR extracted text from financial statements
        
    Returns:
        Dictionary with categorized financial statement sections
    """
    
    # Define section keywords
    section_keywords = {
        'income_statement': ['revenue', 'income', 'profit', 'loss', 'earnings', 'expenses', 'ebitda'],
        'balance_sheet': ['assets', 'liabilities', 'equity', 'capital', 'reserves', 'cash', 'deposits'],
        'cash_flow': ['cash flow', 'operating activities', 'investing activities', 'financing activities'],
        'ratios': ['ratio', 'percentage', 'return on', 'cost income', 'leverage', 'capital adequacy'],
        'performance_metrics': ['eps', 'roe', 'roa', 'nim', 'efficiency', 'productivity']
    }
    
    # Split text into sentences/lines
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    categorized_sections = {section: [] for section in section_keywords.keys()}
    categorized_sections['other'] = []
    
    for line in lines:
        line_lower = line.lower()
        categorized = False
        
        for section, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                categorized_sections[section].append(line)
                categorized = True
                break
        
        if not categorized:
            categorized_sections['other'].append(line)
    
    return categorized_sections

def create_financial_glossary() -> Dict[str, str]:
    """
    Create a glossary of common financial terms and their definitions
    
    Returns:
        Dictionary with term definitions
    """
    
    glossary = {
        'ROE': 'Return on Equity - measures profitability relative to shareholders equity',
        'ROA': 'Return on Assets - measures how efficiently a company uses its assets',
        'EPS': 'Earnings Per Share - net income divided by number of outstanding shares',
        'CET1': 'Common Equity Tier 1 - primary capital adequacy measure for banks',
        'NIM': 'Net Interest Margin - difference between interest earned and paid',
        'Cost Income Ratio': 'Operating expenses as percentage of operating income',
        'Leverage Ratio': 'Measure of financial leverage, debt relative to equity',
        'Basel III': 'International regulatory framework for banks',
        'Tier 1 Capital': 'Core capital that includes equity and retained earnings',
        'Risk Weighted Assets': 'Assets weighted by credit risk for capital calculations',
        'Provision Coverage': 'Loan loss provisions as percentage of non-performing loans',
        'Loan to Deposit Ratio': 'Total loans divided by total deposits',
        'EBITDA': 'Earnings Before Interest, Taxes, Depreciation and Amortization',
        'Working Capital': 'Current assets minus current liabilities',
        'Debt Service Coverage': 'Ability to service debt payments from cash flow'
    }
    
    return glossary

def validate_api_response(response: Dict[str, Any]) -> bool:
    """
    Validate AI API response structure
    
    Args:
        response: API response dictionary
        
    Returns:
        Boolean indicating if response is valid
    """
    
    if not isinstance(response, dict):
        return False
    
    # Check for error conditions
    if 'error' in response:
        return False
    
    # Check for minimum required structure
    required_keys = ['executive_summary', 'key_metrics']
    
    # Allow flexible structure - at least one key section should exist
    valid_sections = ['executive_summary', 'key_metrics', 'balance_sheet', 
                     'financial_ratios', 'analysis', 'trends_analysis']
    
    has_valid_section = any(key in response for key in valid_sections)
    
    return has_valid_section

def clean_financial_text(text: str) -> str:
    """
    Clean and normalize financial text data
    
    Args:
        text: Raw text from OCR or other sources
        
    Returns:
        Cleaned text
    """
    
    if not isinstance(text, str):
        return str(text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Standardize currency formats
    text = re.sub(r'€\s*(\d)', r'EUR \1', text)
    text = re.sub(r'\$\s*(\d)', r'USD \1', text)
    text = re.sub(r'£\s*(\d)', r'GBP \1', text)
    
    # Standardize percentage formats
    text = re.sub(r'(\d+\.?\d*)\s*percent', r'\1%', text)
    
    # Standardize number formats
    text = re.sub(r'(\d+),(\d{3})', r'\1\2', text)  # Remove thousand separators
    
    return text.strip()

# Example usage and testing functions
def test_utilities():
    """Test utility functions with sample data"""
    
    print("Testing Financial Report Analyzer Utilities")
    print("=" * 50)
    
    # Test financial number extraction
    sample_text = "Revenue of EUR 1,638 million increased by 7% compared to previous year. ROE stands at 11.6%."
    extracted = extract_financial_numbers(sample_text)
    print(f"Extracted numbers: {extracted}")
    
    # Test metric standardization
    raw_metrics = {
        "Net Profit": "EUR 690M",
        "return on equity": "11.6%",
        "Cost/Income Ratio": "59.2%"
    }
    standardized = standardize_financial_metrics(raw_metrics)
    print(f"Standardized metrics: {standardized}")
    
    # Test growth rate calculation
    growth = calculate_growth_rates("690", "759")
    print(f"Growth calculation: {growth}")
    
    # Test currency formatting
    formatted = format_currency(1638000000, "EUR")
    print(f"Formatted currency: {formatted}")
    
    print("\n✅ All utility tests completed")

if __name__ == "__main__":
    test_utilities()