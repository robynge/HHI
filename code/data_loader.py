"""
Data loading module for ARK ETF portfolio analysis.
Handles loading portfolio holdings data from Excel files.
"""

import pandas as pd
import numpy as np
import os
import glob


def load_etf_holdings(etf_name='ARKK', file_path=None):
    """
    Load ETF holdings data from Excel file.
    
    Parameters:
    -----------
    etf_name : str
        Name of the ETF (e.g., 'ARKK', 'ARKW', 'ARKQ', 'ARKF', 'ARKG')
    file_path : str, optional
        Path to the Excel file. If None, searches for latest file in parent directory.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: Date, Bloomberg Name, Ticker, Position, Stock_Price, Weight
        
    Raises:
    -------
    FileNotFoundError
        If the specified file does not exist
    """
    if file_path is None:
        # Look in input directory for ETF file
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_dir = os.path.join(parent_dir, 'input')

        # Look for Transformed_Data file in input folder
        file_path = os.path.join(input_dir, f'{etf_name}_Transformed_Data.xlsx')

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No data file found for {etf_name} in {input_dir}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Load data from Excel
    print(f"Loading {etf_name} data from {file_path}...")
    etf_data = pd.read_excel(file_path, sheet_name='Sheet1')
    
    # Convert Date column to datetime
    etf_data['Date'] = pd.to_datetime(etf_data['Date'])
    
    # Ensure required columns exist
    required_cols = ['Date', 'Bloomberg Name', 'Ticker', 'Position', 'Stock_Price', 'Weight']
    missing_cols = [col for col in required_cols if col not in etf_data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Convert Weight to decimal if it's in percentage
    if etf_data['Weight'].max() > 1:
        etf_data['Weight'] = etf_data['Weight'] / 100
    
    # Sort by date
    etf_data = etf_data.sort_values('Date')
    
    print(f"Loaded {len(etf_data)} records from {file_path}")
    return etf_data


def load_arkk_holdings(file_path=None):
    """
    Legacy function - loads ARKK holdings data.
    Maintained for backward compatibility.
    """
    return load_etf_holdings('ARKK', file_path)


def filter_data_by_date(data, start_date=None, end_date=None):
    """
    Filter dataframe by date range.
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame with Date column
    start_date : str or pd.Timestamp, optional
        Start date for filtering
    end_date : str or pd.Timestamp, optional
        End date for filtering
        
    Returns:
    --------
    pd.DataFrame
        Filtered DataFrame
    """
    filtered_data = data.copy()
    
    if start_date is not None:
        start_date = pd.to_datetime(start_date)
        filtered_data = filtered_data[filtered_data['Date'] >= start_date]
    
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
        filtered_data = filtered_data[filtered_data['Date'] <= end_date]
    
    return filtered_data


def get_date_range(data):
    """
    Get the date range of the data.
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame with Date column
        
    Returns:
    --------
    tuple
        (min_date, max_date) as formatted strings
    """
    min_date = data['Date'].min().strftime('%Y-%m-%d')
    max_date = data['Date'].max().strftime('%Y-%m-%d')
    return min_date, max_date