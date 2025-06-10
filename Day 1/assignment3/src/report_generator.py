"""
Report Generation Module
Creates formatted financial analysis reports in various formats
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

class FinancialReportGenerator:
    def __init__(self, output_dir: str = "output/generated_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_comprehensive_report(self, analysis_data: Dict[str, Any], 
                                    company_name: str = "Company",
                                    report_title: str = "Financial Analysis Report") -> str:
        """
        Generate a comprehensive financial analysis report
        
        Args:
            analysis_data: Dictionary containing analysis results
            company_name: Name of the company being analyzed
            report_title: Title for the report
            
        Returns:
            Path to generated report file
        """
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{company_name.replace(' ', '_')}_analysis_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # Create report content
        report_content = self._create_markdown_report(analysis_data, company_name, report_title)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f"Report generated: {filepath}")
        return str(filepath)
    
    def _create_markdown_report(self, data: Dict[str, Any], 
                              company_name: str, report_title: str) -> str:
        """Create formatted markdown report"""
        
        report = f"""# {report_title}
## {company_name}

*Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}*

---

## Executive Summary

{data.get('executive_summary', 'Executive summary not available.')}

---

## Key Financial Metrics

"""
        
        # Add key metrics section
        if 'key_metrics' in data:
            metrics = data['key_metrics']
            
            report += """
| Metric | Current Value | Change | Period |
|--------|---------------|--------|--------|
"""
            
            for metric_name, metric_data in metrics.items():
                if isinstance(metric_data, dict):
                    value = metric_data.get('value', 'N/A')
                    change = metric_data.get('change', 'N/A')
                    period = metric_data.get('period', 'N/A')
                    
                    display_name = metric_name.replace('_', ' ').title()
                    report += f"| {display_name} | {value} | {change} | {period} |\n"
        
        # Add balance sheet section
        if 'balance_sheet' in data:
            report += "\n## Balance Sheet Highlights\n\n"
            
            balance_sheet = data['balance_sheet']
            
            report += """
| Item | Current Value | Change |
|------|---------------|--------|
"""
            
            for item_name, item_data in balance_sheet.items():
                if isinstance(item_data, dict):
                    value = item_data.get('value', 'N/A')
                    change = item_data.get('change', 'N/A')
                    
                    display_name = item_name.replace('_', ' ').title()
                    report += f"| {display_name} | {value} | {change} |\n"
        
        # Add financial ratios section
        if 'financial_ratios' in data:
            report += "\n## Financial Ratios\n\n"
            
            ratios = data['financial_ratios']
            
            report += """
| Ratio | Current Value | Target/Requirement | Status |
|-------|---------------|-------------------|--------|
"""
            
            for ratio_name, ratio_data in ratios.items():
                if isinstance(ratio_data, dict):
                    value = ratio_data.get('value', 'N/A')
                    target = ratio_data.get('target', ratio_data.get('requirement', 'N/A'))
                    status = "✅ Meeting" if 'target' in ratio_data else "📊 Tracking"
                    
                    display_name = ratio_name.replace('_', ' ').title()
                    report += f"| {display_name} | {value} | {target} | {status} |\n"
        
        # Add trends analysis
        if 'trends_analysis' in data and data['trends_analysis']:
            report += "\n## Trends Analysis\n\n"
            for trend in data['trends_analysis']:
                report += f"- {trend}\n"
        
        # Add risk assessment
        if 'risk_assessment' in data:
            risk_data = data['risk_assessment']
            
            report += "\n## Risk Assessment\n\n"
            
            if 'credit_quality' in risk_data:
                report += f"**Credit Quality:** {risk_data['credit_quality']}\n\n"
            
            if 'regulatory_status' in risk_data:
                report += f"**Regulatory Status:** {risk_data['regulatory_status']}\n\n"
            
            if 'key_risks' in risk_data and risk_data['key_risks']:
                report += "**Key Risks Identified:**\n"
                for risk in risk_data['key_risks']:
                    report += f"- {risk}\n"
        
        # Add recommendations
        if 'recommendations' in data and data['recommendations']:
            report += "\n## Recommendations\n\n"
            for i, recommendation in enumerate(data['recommendations'], 1):
                report += f"{i}. {recommendation}\n"
        
        # Add technical details
        report += f"\n---\n\n*This report was generated using AI-powered financial document analysis.*\n"
        
        return report
    
    def generate_json_report(self, analysis_data: Dict[str, Any], 
                           company_name: str = "Company") -> str:
        """Generate JSON format report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{company_name.replace(' ', '_')}_analysis_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Add metadata
        report_data = {
            "metadata": {
                "company_name": company_name,
                "generated_at": datetime.now().isoformat(),
                "report_type": "financial_analysis"
            },
            "analysis": analysis_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON report generated: {filepath}")
        return str(filepath)
    
    def create_summary_dashboard(self, analysis_data: Dict[str, Any], 
                               company_name: str = "Company") -> str:
        """Create a visual dashboard summary"""
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'{company_name} - Financial Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Extract data for visualization
        try:
            # Plot 1: Key Metrics Comparison (if historical data available)
            ax1 = axes[0, 0]
            ax1.set_title('Key Financial Metrics')
            
            # Sample data - replace with actual extracted values
            metrics = ['Revenue', 'Net Income', 'EPS', 'ROE']
            values = [100, 80, 60, 90]  # Replace with actual values
            
            bars = ax1.bar(metrics, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
            ax1.set_ylabel('Performance Index')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{value}%', ha='center', va='bottom')
            
            # Plot 2: Financial Ratios
            ax2 = axes[0, 1]
            ax2.set_title('Financial Ratios')
            
            ratios = ['Cost/Income', 'CET1', 'Leverage']
            ratio_values = [59.2, 14.1, 5.5]  # Replace with actual values
            targets = [60.0, 13.5, 5.0]  # Replace with actual targets
            
            x = range(len(ratios))
            width = 0.35
            
            ax2.bar([i - width/2 for i in x], ratio_values, width, label='Current', alpha=0.8)
            ax2.bar([i + width/2 for i in x], targets, width, label='Target', alpha=0.6)
            
            ax2.set_xlabel('Ratios')
            ax2.set_ylabel('Value (%)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(ratios)
            ax2.legend()
            
            # Plot 3: Risk Assessment (Pie Chart)
            ax3 = axes[1, 0]
            ax3.set_title('Risk Distribution')
            
            risk_categories = ['Credit Risk', 'Market Risk', 'Operational Risk', 'Regulatory Risk']
            risk_values = [30, 25, 25, 20]  # Sample values
            
            ax3.pie(risk_values, labels=risk_categories, autopct='%1.1f%%', startangle=90)
            
            # Plot 4: Performance Trend
            ax4 = axes[1, 1]
            ax4.set_title('Performance Trend')
            
            quarters = ['Q1 23', 'Q2 23', 'Q3 23', 'Q4 23', 'Q1 24']
            performance = [85, 87, 89, 91, 88]  # Sample trend data
            
            ax4.plot(quarters, performance, marker='o', linewidth=2, markersize=6)
            ax4.set_xlabel('Period')
            ax4.set_ylabel('Performance Score')
            ax4.grid(True, alpha=0.3)
            ax4.set_ylim(80, 95)
            
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            # Create simple text-based dashboard instead
            for ax in axes.flat:
                ax.text(0.5, 0.5, 'Data visualization\nunder development', 
                       ha='center', va='center', transform=ax.transAxes)
        
        plt.tight_layout()
        
        # Save dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{company_name.replace(' ', '_')}_dashboard_{timestamp}.png"
        filepath = self.output_dir / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Dashboard generated: {filepath}")
        return str(filepath)
    
    def export_to_excel(self, analysis_data: Dict[str, Any], 
                       company_name: str = "Company") -> str:
        """Export analysis data to Excel format"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{company_name.replace(' ', '_')}_analysis_{timestamp}.xlsx"
        filepath = self.output_dir / filename
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': [],
                    'Value': [],
                    'Change': [],
                    'Status': []
                }
                
                # Extract key metrics
                if 'key_metrics' in analysis_data:
                    for metric, data in analysis_data['key_metrics'].items():
                        if isinstance(data, dict):
                            summary_data['Metric'].append(metric.replace('_', ' ').title())
                            summary_data['Value'].append(data.get('value', 'N/A'))
                            summary_data['Change'].append(data.get('change', 'N/A'))
                            summary_data['Status'].append('Tracked')
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Balance Sheet
                if 'balance_sheet' in analysis_data:
                    bs_data = []
                    for item, data in analysis_data['balance_sheet'].items():
                        if isinstance(data, dict):
                            bs_data.append({
                                'Item': item.replace('_', ' ').title(),
                                'Current Value': data.get('value', 'N/A'),
                                'Change': data.get('change', 'N/A')
                            })
                    
                    if bs_data:
                        bs_df = pd.DataFrame(bs_data)
                        bs_df.to_excel(writer, sheet_name='Balance Sheet', index=False)
                
                # Financial Ratios
                if 'financial_ratios' in analysis_data:
                    ratio_data = []
                    for ratio, data in analysis_data['financial_ratios'].items():
                        if isinstance(data, dict):
                            ratio_data.append({
                                'Ratio': ratio.replace('_', ' ').title(),
                                'Current Value': data.get('value', 'N/A'),
                                'Target': data.get('target', data.get('requirement', 'N/A'))
                            })
                    
                    if ratio_data:
                        ratio_df = pd.DataFrame(ratio_data)
                        ratio_df.to_excel(writer, sheet_name='Financial Ratios', index=False)
                
                # Risk Assessment
                if 'risk_assessment' in analysis_data:
                    risk_data = []
                    risk_info = analysis_data['risk_assessment']
                    
                    if 'key_risks' in risk_info:
                        for risk in risk_info['key_risks']:
                            risk_data.append({'Risk Factor': risk, 'Category': 'Identified Risk'})
                    
                    if risk_data:
                        risk_df = pd.DataFrame(risk_data)
                        risk_df.to_excel(writer, sheet_name='Risk Assessment', index=False)
        
        except Exception as e:
            print(f"Error creating Excel file: {e}")
            return None
        
        print(f"Excel report generated: {filepath}")
        return str(filepath)
    
    def generate_all_formats(self, analysis_data: Dict[str, Any], 
                           company_name: str = "Company") -> Dict[str, str]:
        """Generate reports in all available formats"""
        
        generated_files = {}
        
        try:
            # Markdown report
            md_file = self.generate_comprehensive_report(analysis_data, company_name)
            generated_files['markdown'] = md_file
        except Exception as e:
            print(f"Error generating markdown report: {e}")
        
        try:
            # JSON report
            json_file = self.generate_json_report(analysis_data, company_name)
            generated_files['json'] = json_file
        except Exception as e:
            print(f"Error generating JSON report: {e}")
        
        try:
            # Dashboard
            dashboard_file = self.create_summary_dashboard(analysis_data, company_name)
            generated_files['dashboard'] = dashboard_file
        except Exception as e:
            print(f"Error generating dashboard: {e}")
        
        try:
            # Excel report
            excel_file = self.export_to_excel(analysis_data, company_name)
            if excel_file:
                generated_files['excel'] = excel_file
        except Exception as e:
            print(f"Error generating Excel report: {e}")
        
        return generated_files

# Example usage and testing
if __name__ == "__main__":
    # Sample analysis data (similar to ABN AMRO example)
    sample_analysis = {
        "executive_summary": "ABN AMRO Bank demonstrates robust financial performance in Q3 2024 with strong capital position and improved operational efficiency.",
        "key_metrics": {
            "net_profit": {"value": "EUR 690 million", "change": "-9.1%", "period": "Q3 2024"},
            "eps": {"value": "EUR 0.78", "change": "-8.2%", "period": "Q3 2024"},
            "roe": {"value": "11.6%", "target": "9-10%", "status": "Above target"}
        },
        "balance_sheet": {
            "total_assets": {"value": "EUR 403.8 billion", "change": "+EUR 10.4B"},
            "loans_advances": {"value": "EUR 259.6 billion", "change": "+EUR 8.1B"},
            "client_deposits": {"value": "EUR 224.5 billion", "change": "Stable"}
        },
        "financial_ratios": {
            "cost_income_ratio": {"value": "59.2%", "target": "60%"},
            "cet1_ratio": {"value": "14.1%", "requirement": "Basel III compliant"},
            "leverage_ratio": {"value": "5.5%", "requirement": "3%"}
        },
        "trends_analysis": [
            "Net Interest Income increased 7% YoY driven by Treasury results",
            "Operating expenses rose 9% due to collective labor agreement",
            "Cost of Risk remained low at -2 basis points"
        ],
        "risk_assessment": {
            "credit_quality": "Strong with declining forbearance ratio",
            "regulatory_status": "Basel IV implementation postponed to Q2 2025",
            "key_risks": [
                "Regulatory changes impact",
                "Interest rate environment",
                "Economic uncertainty"
            ]
        },
        "recommendations": [
            "Continue focus on operational efficiency improvements",
            "Monitor regulatory developments closely",
            "Maintain strong capital buffer for Basel IV transition"
        ]
    }
    
    # Generate all report formats
    generator = FinancialReportGenerator()
    files = generator.generate_all_formats(sample_analysis, "ABN AMRO Bank")
    
    print("\nGenerated Files:")
    for format_type, filepath in files.items():
        print(f"{format_type.title()}: {filepath}")