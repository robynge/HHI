"""
Simplified ETF HHI Analysis with Daily Tracking
"""

import warnings
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Import modules
from data_loader import load_etf_holdings, get_date_range
from metrics import calculate_holdings_hhi, calculate_pnl_for_period
from portfolio_changes import track_portfolio_changes
from weight_changes import calculate_weight_changes, create_daily_weight_change_summary

# Suppress warnings
warnings.filterwarnings('ignore')

# ========================
# CONFIGURATION
# ========================
ETFS_TO_ANALYZE = ['ARKK', 'ARKW', 'ARKQ', 'ARKF', 'ARKG', 'ARKX']  # Analyze all available ETFs in input folder

# Analysis period
ANALYSIS_PERIOD = {
    'start': '2024-04-01',
    'end': datetime.now().strftime('%Y-%m-%d')  # Today
}

# ========================
# ANALYSIS FUNCTIONS
# ========================

def calculate_daily_hhi_and_contributors(etf_data, start_date, end_date):
    """
    Calculate daily HHI and identify top profit contributors.
    
    Returns:
    --------
    pd.DataFrame with columns:
    - Date
    - HHI
    - Holdings_Count
    - Top_50pct_Profit_Count
    - Top_50pct_Profit_Tickers
    """
    # Filter data by date range
    if start_date:
        etf_data = etf_data[etf_data['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        etf_data = etf_data[etf_data['Date'] <= pd.to_datetime(end_date)]
    
    # Sort by date
    etf_data = etf_data.sort_values('Date')
    unique_dates = sorted(etf_data['Date'].unique())
    
    results = []
    
    for i, current_date in enumerate(unique_dates):
        if i == 0:
            # First day - no P&L to calculate
            daily_holdings = etf_data[etf_data['Date'] == current_date]
            hhi = calculate_holdings_hhi(daily_holdings)
            holdings_count = len(daily_holdings[~daily_holdings['Ticker'].isin(['XX', 'MVRXX', 'DGCXX', 'FEDXX'])])
            
            results.append({
                'Date': current_date.strftime('%m/%d/%Y'),
                'HHI': hhi,
                'Holdings_Count': holdings_count,
                'Top_50pct_Profit_Count': 0,
                'Top_50pct_Profit_Tickers': ''
            })
        else:
            # Calculate HHI
            daily_holdings = etf_data[etf_data['Date'] == current_date]
            hhi = calculate_holdings_hhi(daily_holdings)
            holdings_count = len(daily_holdings[~daily_holdings['Ticker'].isin(['XX', 'MVRXX', 'DGCXX', 'FEDXX'])])
            
            # Calculate P&L from previous day
            prev_date = unique_dates[i-1]
            prev_holdings = etf_data[etf_data['Date'] == prev_date]
            
            pnl_data = calculate_pnl_for_period(prev_holdings, daily_holdings)
            
            # Find top 50% profit contributors
            if pnl_data:
                # Get only positive P&L stocks
                positive_pnl = {ticker: data['pnl'] for ticker, data in pnl_data.items() if data['pnl'] > 0}
                
                if positive_pnl:
                    # Sort by P&L
                    sorted_positive = sorted(positive_pnl.items(), key=lambda x: x[1], reverse=True)
                    total_positive_pnl = sum(p for _, p in sorted_positive)
                    
                    # Find stocks that contribute to 50% of positive P&L
                    cumulative_pnl = 0
                    top_50pct_tickers = []
                    
                    for ticker, pnl in sorted_positive:
                        cumulative_pnl += pnl
                        top_50pct_tickers.append(ticker)
                        if cumulative_pnl >= total_positive_pnl * 0.5:
                            break
                    
                    top_50pct_count = len(top_50pct_tickers)
                    top_50pct_names = ', '.join(top_50pct_tickers)
                else:
                    top_50pct_count = 0
                    top_50pct_names = ''
            else:
                top_50pct_count = 0
                top_50pct_names = ''
            
            results.append({
                'Date': current_date.strftime('%m/%d/%Y'),
                'HHI': hhi,
                'Holdings_Count': holdings_count,
                'Top_50pct_Profit_Count': top_50pct_count,
                'Top_50pct_Profit_Tickers': top_50pct_names
            })
    
    return pd.DataFrame(results)


def analyze_etf(etf_name, start_date, end_date):
    """
    Analyze a single ETF and create Excel output.
    """
    print(f"\n{'='*60}")
    print(f"Analyzing {etf_name}")
    print(f"{'='*60}")
    
    # Load ETF data
    try:
        etf_data = load_etf_holdings(etf_name)
    except Exception as e:
        print(f"❌ Error loading {etf_name}: {e}")
        return
    
    # Get date range
    data_start, data_end = get_date_range(etf_data)
    print(f"Data available from {data_start} to {data_end}")
    print(f"Analyzing period: {start_date} to {end_date}")
    
    # Calculate daily HHI and contributors
    print("Calculating daily HHI and profit contributors...")
    daily_analysis = calculate_daily_hhi_and_contributors(etf_data, start_date, end_date)
    
    # Track portfolio changes
    print("Tracking portfolio changes...")
    additions_matrix, removals_matrix, changes_summary = track_portfolio_changes(etf_data, start_date, end_date)
    
    # Calculate weight changes
    print("Calculating weight changes...")
    weight_changes_df = calculate_weight_changes(etf_data, start_date, end_date)
    
    # Create daily changes summary
    daily_changes = []
    # Need to match date from changes_summary with formatted date
    for date_str in daily_analysis['Date'].unique():
        # Convert string back to datetime for matching (mm/dd/yyyy format)
        date_parts = date_str.split('/')
        date_dt = pd.to_datetime(f"{date_parts[2]}-{date_parts[0]}-{date_parts[1]}")
        date_changes = changes_summary[changes_summary['Date'] == date_dt]
        
        added = date_changes[date_changes['Action'] == 'Added']['Ticker'].tolist()
        removed = date_changes[date_changes['Action'] == 'Removed']['Ticker'].tolist()
        
        # Convert to strings
        added = [str(t) for t in added]
        removed = [str(t) for t in removed]
        
        if added or removed:
            daily_changes.append({
                'Date': date_str,  # Use the formatted date string
                'Stocks_Added': ', '.join(added) if added else '',
                'Stocks_Added_Count': len(added),
                'Stocks_Removed': ', '.join(removed) if removed else '',
                'Stocks_Removed_Count': len(removed)
            })
    
    daily_changes_df = pd.DataFrame(daily_changes) if daily_changes else pd.DataFrame()
    
    # Export to Excel
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f'{etf_name}_Analysis_{datetime.now().strftime("%Y%m%d")}.xlsx')
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Daily HHI and Contributors
        daily_analysis.to_excel(writer, sheet_name='Daily_HHI_Analysis', index=False)
        
        # Sheet 2: Portfolio Changes
        if not daily_changes_df.empty:
            daily_changes_df.to_excel(writer, sheet_name='Portfolio_Changes', index=False)
        else:
            # Create empty sheet with headers
            pd.DataFrame(columns=['Date', 'Stocks_Added', 'Stocks_Added_Count', 
                                 'Stocks_Removed', 'Stocks_Removed_Count']).to_excel(
                writer, sheet_name='Portfolio_Changes', index=False)
        
        # Sheet 3: Weight Changes Analysis
        if not weight_changes_df.empty:
            weight_changes_df.to_excel(writer, sheet_name='Weight_Changes', index=False)
    
    print(f"✅ Exported to: {output_file}")
    
    # Print summary statistics
    print(f"\nSummary Statistics:")
    print(f"  Average HHI: {daily_analysis['HHI'].mean():.4f}")
    print(f"  Min HHI: {daily_analysis['HHI'].min():.4f}")
    print(f"  Max HHI: {daily_analysis['HHI'].max():.4f}")
    print(f"  Average Holdings: {daily_analysis['Holdings_Count'].mean():.1f}")
    print(f"  Days with top contributors: {(daily_analysis['Top_50pct_Profit_Count'] > 0).sum()}")
    
    if not daily_changes_df.empty:
        print(f"  Total stocks added: {daily_changes_df['Stocks_Added_Count'].sum()}")
        print(f"  Total stocks removed: {daily_changes_df['Stocks_Removed_Count'].sum()}")


def main():
    """
    Main function to run analysis for all ETFs.
    """
    print("🔍 ETF HHI and Portfolio Analysis")
    print(f"ETFs to analyze: {', '.join(ETFS_TO_ANALYZE)}")
    print(f"Analysis period: {ANALYSIS_PERIOD['start']} to {ANALYSIS_PERIOD['end']}")
    
    for etf_name in ETFS_TO_ANALYZE:
        analyze_etf(etf_name, ANALYSIS_PERIOD['start'], ANALYSIS_PERIOD['end'])
    
    print("\n" + "="*60)
    print("✅ All analyses complete!")
    print("="*60)


if __name__ == "__main__":
    main()