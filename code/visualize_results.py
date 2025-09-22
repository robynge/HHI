"""
Visualization script for ETF HHI Analysis results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def plot_hhi_over_time(df, etf_name, output_dir):
    """
    Create line plot for HHI over time
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Plot HHI
    ax.plot(df['Date'], df['HHI'], linewidth=2, color='navy', alpha=0.8)
    
    # Formatting
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('HHI (Herfindahl-Hirschman Index)', fontsize=12)
    ax.set_title(f'{etf_name} Portfolio Concentration (HHI) Over Time', fontsize=14, fontweight='bold')
    
    # Set y-axis limits
    ax.set_ylim(0, 0.1)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add horizontal lines for concentration levels
    ax.axhline(y=0.01, color='green', linestyle=':', alpha=0.5, label='Highly Diversified (<0.01)')
    ax.axhline(y=0.15, color='orange', linestyle=':', alpha=0.5, label='Moderately Concentrated (0.15)')
    ax.axhline(y=0.25, color='red', linestyle=':', alpha=0.5, label='Highly Concentrated (>0.25)')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)
    
    # Add legend
    ax.legend(loc='upper right')
    
    # Add statistics text
    stats_text = f'Mean: {df["HHI"].mean():.4f}\nMin: {df["HHI"].min():.4f}\nMax: {df["HHI"].max():.4f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    output_file = os.path.join(output_dir, f'{etf_name}_HHI_TimeSeries.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ HHI time series plot saved to: {output_file}")


def plot_top_contributors_frequency(df, etf_name, output_dir):
    """
    Create bar plot for frequency of tickers contributing >50% of daily profits
    """
    # Extract all tickers from Top_50pct_Profit_Tickers column
    all_tickers = []
    for tickers_str in df['Top_50pct_Profit_Tickers']:
        if pd.notna(tickers_str) and tickers_str != '':
            tickers = [t.strip() for t in str(tickers_str).split(',')]
            all_tickers.extend(tickers)
    
    if not all_tickers:
        print(f"  ⚠ No top contributor data found for {etf_name}")
        return
    
    # Count frequency
    ticker_counts = pd.Series(all_tickers).value_counts()
    
    # Select top 20 for better visualization
    top_20 = ticker_counts.head(20)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create bar plot
    bars = ax.bar(range(len(top_20)), top_20.values, color='steelblue', alpha=0.8)
    
    # Color gradient for bars
    colors = plt.cm.coolwarm(np.linspace(0.3, 0.7, len(bars)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Set x-axis labels
    ax.set_xticks(range(len(top_20)))
    ax.set_xticklabels(top_20.index, rotation=45, ha='right')
    
    # Labels and title
    ax.set_xlabel('Stock Ticker', fontsize=12)
    ax.set_ylabel('Days as Top Contributor (>50% of daily profits)', fontsize=12)
    ax.set_title(f'{etf_name} - Frequency of Top Profit Contributors', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, top_20.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(value), ha='center', va='bottom', fontsize=9)
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add statistics
    total_days = (df['Top_50pct_Profit_Count'] > 0).sum()
    stats_text = f'Total days with data: {total_days}\nUnique top contributors: {len(ticker_counts)}'
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    output_file = os.path.join(output_dir, f'{etf_name}_Top_Contributors_Frequency.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Top contributors frequency plot saved to: {output_file}")


def main():
    """
    Main function to generate visualizations for all ETFs
    """
    print("\n📊 Generating Visualizations for ETF Analysis")
    print("=" * 60)
    
    # Setup paths
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    
    # Get all Excel files from today
    today_str = datetime.now().strftime("%Y%m%d")
    excel_files = [f for f in os.listdir(output_dir) 
                   if f.endswith(f'_{today_str}.xlsx') and not f.startswith('~$')]
    
    if not excel_files:
        print("❌ No analysis files found from today. Please run main.py first.")
        return
    
    # Process each ETF
    for excel_file in excel_files:
        etf_name = excel_file.split('_')[0]
        print(f"\nProcessing {etf_name}...")
        
        # Read Excel file
        excel_path = os.path.join(output_dir, excel_file)
        df = pd.read_excel(excel_path, sheet_name='Daily_HHI_Analysis')
        
        # Generate plots
        plot_hhi_over_time(df, etf_name, output_dir)
        plot_top_contributors_frequency(df, etf_name, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ All visualizations complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()