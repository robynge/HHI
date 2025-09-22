"""
Portfolio changes tracking module.
Tracks when stocks are added to or removed from the portfolio.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


def track_portfolio_changes(etf_data, start_date=None, end_date=None):
    """
    Track daily portfolio additions and removals.
    
    Parameters:
    -----------
    etf_data : pd.DataFrame
        ETF holdings data with Date, Ticker columns
    start_date : str, optional
        Start date for analysis
    end_date : str, optional
        End date for analysis
        
    Returns:
    --------
    tuple of (additions_df, removals_df, changes_summary_df)
        - additions_df: DataFrame with dates as rows, tickers as columns (1 = added that day)
        - removals_df: DataFrame with dates as rows, tickers as columns (1 = removed that day)
        - changes_summary_df: Summary DataFrame with date, action, and ticker
    """
    # Filter by date range if specified
    if start_date:
        etf_data = etf_data[etf_data['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        etf_data = etf_data[etf_data['Date'] <= pd.to_datetime(end_date)]
    
    # Sort by date
    etf_data = etf_data.sort_values('Date')
    
    # Get unique dates
    unique_dates = sorted(etf_data['Date'].unique())
    
    # Skip cash funds
    cash_funds = ['XX', 'MVRXX', 'DGCXX', 'FEDXX']
    etf_data = etf_data[~etf_data['Ticker'].isin(cash_funds)]
    
    # Track changes
    additions_dict = {}
    removals_dict = {}
    changes_list = []
    
    # Process each date
    for i, current_date in enumerate(unique_dates):
        if i == 0:
            # First date - all positions are considered "new"
            current_tickers = set(etf_data[etf_data['Date'] == current_date]['Ticker'].unique())
            for ticker in current_tickers:
                changes_list.append({
                    'Date': current_date,
                    'Action': 'Initial',
                    'Ticker': ticker
                })
        else:
            # Compare with previous date
            prev_date = unique_dates[i-1]
            
            prev_tickers = set(etf_data[etf_data['Date'] == prev_date]['Ticker'].unique())
            current_tickers = set(etf_data[etf_data['Date'] == current_date]['Ticker'].unique())
            
            # Find additions (in current but not in previous)
            added_tickers = current_tickers - prev_tickers
            
            # Find removals (in previous but not in current)
            removed_tickers = prev_tickers - current_tickers
            
            # Record additions
            if added_tickers:
                if current_date not in additions_dict:
                    additions_dict[current_date] = []
                for ticker in added_tickers:
                    additions_dict[current_date].append(ticker)
                    changes_list.append({
                        'Date': current_date,
                        'Action': 'Added',
                        'Ticker': ticker
                    })
            
            # Record removals
            if removed_tickers:
                if current_date not in removals_dict:
                    removals_dict[current_date] = []
                for ticker in removed_tickers:
                    removals_dict[current_date].append(ticker)
                    changes_list.append({
                        'Date': current_date,
                        'Action': 'Removed',
                        'Ticker': ticker
                    })
    
    # Create summary DataFrame
    changes_summary_df = pd.DataFrame(changes_list)
    
    # Create additions matrix (dates x tickers)
    all_added_tickers = set()
    for tickers in additions_dict.values():
        all_added_tickers.update(tickers)
    
    additions_matrix = pd.DataFrame(index=unique_dates[1:], columns=sorted([str(t) for t in all_added_tickers]))
    additions_matrix = additions_matrix.fillna(0)
    
    for date, tickers in additions_dict.items():
        for ticker in tickers:
            if date in additions_matrix.index and ticker in additions_matrix.columns:
                additions_matrix.loc[date, ticker] = 1
    
    # Create removals matrix (dates x tickers)
    all_removed_tickers = set()
    for tickers in removals_dict.values():
        all_removed_tickers.update(tickers)
    
    removals_matrix = pd.DataFrame(index=unique_dates[1:], columns=sorted([str(t) for t in all_removed_tickers]))
    removals_matrix = removals_matrix.fillna(0)
    
    for date, tickers in removals_dict.items():
        for ticker in tickers:
            if date in removals_matrix.index and ticker in removals_matrix.columns:
                removals_matrix.loc[date, ticker] = 1
    
    # Clean up matrices - keep only rows with changes
    additions_matrix = additions_matrix[additions_matrix.sum(axis=1) > 0]
    removals_matrix = removals_matrix[removals_matrix.sum(axis=1) > 0]
    
    return additions_matrix, removals_matrix, changes_summary_df


def create_portfolio_changes_report(etf_data, etf_name, start_date=None, end_date=None):
    """
    Create a comprehensive portfolio changes report.
    
    Parameters:
    -----------
    etf_data : pd.DataFrame
        ETF holdings data
    etf_name : str
        Name of the ETF
    start_date : str, optional
        Start date for analysis
    end_date : str, optional
        End date for analysis
        
    Returns:
    --------
    dict
        Dictionary with report DataFrames
    """
    # Track changes
    additions_matrix, removals_matrix, changes_summary = track_portfolio_changes(
        etf_data, start_date, end_date
    )
    
    # Create daily summary
    daily_summary = []
    
    for date in changes_summary['Date'].unique():
        date_changes = changes_summary[changes_summary['Date'] == date]
        
        added = date_changes[date_changes['Action'] == 'Added']['Ticker'].tolist()
        removed = date_changes[date_changes['Action'] == 'Removed']['Ticker'].tolist()
        
        if added or removed:
            daily_summary.append({
                'Date': date,
                'Additions': len(added),
                'Removals': len(removed),
                'Added_Tickers': ', '.join(added) if added else '',
                'Removed_Tickers': ', '.join(removed) if removed else ''
            })
    
    daily_summary_df = pd.DataFrame(daily_summary)
    
    # Calculate statistics
    if start_date and end_date:
        period_str = f"{start_date} to {end_date}"
    else:
        period_str = "Full History"
    
    # Count unique stocks
    all_dates = sorted(changes_summary['Date'].unique())
    if len(all_dates) > 0:
        first_date_stocks = set(changes_summary[
            (changes_summary['Date'] == all_dates[0]) & 
            (changes_summary['Action'] == 'Initial')
        ]['Ticker'])
        
        total_added = len(changes_summary[changes_summary['Action'] == 'Added'])
        total_removed = len(changes_summary[changes_summary['Action'] == 'Removed'])
        
        stats_df = pd.DataFrame([{
            'ETF': etf_name,
            'Period': period_str,
            'Start_Date': all_dates[0] if len(all_dates) > 0 else None,
            'End_Date': all_dates[-1] if len(all_dates) > 0 else None,
            'Initial_Holdings': len(first_date_stocks),
            'Total_Additions': total_added,
            'Total_Removals': total_removed,
            'Net_Change': total_added - total_removed,
            'Days_With_Changes': len(daily_summary_df)
        }])
    else:
        stats_df = pd.DataFrame()
    
    return {
        'additions_matrix': additions_matrix,
        'removals_matrix': removals_matrix,
        'changes_summary': changes_summary,
        'daily_summary': daily_summary_df,
        'statistics': stats_df
    }


def export_portfolio_changes(etf_name, report_data, output_dir=None):
    """
    Export portfolio changes report to Excel.
    
    Parameters:
    -----------
    etf_name : str
        Name of the ETF
    report_data : dict
        Dictionary with report DataFrames from create_portfolio_changes_report
    output_dir : str, optional
        Output directory path
        
    Returns:
    --------
    str
        Path to the exported Excel file
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"{etf_name}_Portfolio_Changes_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Export to Excel with multiple sheets
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Statistics sheet
        if not report_data['statistics'].empty:
            report_data['statistics'].to_excel(
                writer, sheet_name='Summary', index=False
            )
        
        # Daily summary sheet
        if not report_data['daily_summary'].empty:
            report_data['daily_summary'].to_excel(
                writer, sheet_name='Daily_Changes', index=False
            )
        
        # Additions matrix
        if not report_data['additions_matrix'].empty:
            report_data['additions_matrix'].to_excel(
                writer, sheet_name='Additions_Matrix'
            )
        
        # Removals matrix
        if not report_data['removals_matrix'].empty:
            report_data['removals_matrix'].to_excel(
                writer, sheet_name='Removals_Matrix'
            )
        
        # Full changes log
        if not report_data['changes_summary'].empty:
            report_data['changes_summary'].to_excel(
                writer, sheet_name='All_Changes', index=False
            )
    
    print(f"📊 Exported portfolio changes to: {filepath}")
    
    return filepath