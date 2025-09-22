"""
Weight changes analysis module.
Tracks daily weight changes and decomposes them into position and price components.
"""

import pandas as pd
import numpy as np


def calculate_weight_changes(etf_data, start_date=None, end_date=None):
    """
    Calculate daily weight changes for each stock and decompose into position/price components.
    
    Parameters:
    -----------
    etf_data : pd.DataFrame
        ETF holdings data with Date, Ticker, Weight, Position, Stock_Price, Market Value columns
    start_date : str, optional
        Start date for analysis
    end_date : str, optional
        End date for analysis
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with weight change analysis for each stock on each date
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
    
    results = []
    
    # Process each date pair
    for i in range(1, len(unique_dates)):
        current_date = unique_dates[i]
        prev_date = unique_dates[i-1]
        
        # Get holdings for both dates
        prev_holdings = etf_data[etf_data['Date'] == prev_date]
        current_holdings = etf_data[etf_data['Date'] == current_date]
        
        # Calculate total market value for previous date (for denominator)
        # Use ETF Market Value which is the total portfolio value
        prev_total_market_value = prev_holdings['ETF Market Value'].iloc[0] if len(prev_holdings) > 0 else 0
        
        # Get all unique tickers from both dates
        all_tickers = set(prev_holdings['Ticker'].unique()) | set(current_holdings['Ticker'].unique())
        
        for ticker in all_tickers:
            # Skip if ticker is NaN or cash fund
            if pd.isna(ticker) or (isinstance(ticker, str) and ticker in cash_funds):
                continue
            
            # Get data for this ticker on both dates
            prev_ticker_data = prev_holdings[prev_holdings['Ticker'] == ticker]
            current_ticker_data = current_holdings[current_holdings['Ticker'] == ticker]
            
            # Initialize values
            prev_weight = 0
            prev_position = 0
            prev_price = 0
            current_weight = 0
            current_position = 0
            current_price = 0
            company_name = ''
            
            # Get previous date values
            if len(prev_ticker_data) > 0:
                prev_row = prev_ticker_data.iloc[0]
                prev_weight = prev_row['Weight']
                prev_position = prev_row['Position']
                prev_price = prev_row['Stock_Price']
                if 'Company_Name' in prev_row:
                    company_name = prev_row['Company_Name']
            
            # Get current date values
            if len(current_ticker_data) > 0:
                current_row = current_ticker_data.iloc[0]
                current_weight = current_row['Weight']
                current_position = current_row['Position']
                current_price = current_row['Stock_Price']
                if 'Company_Name' in current_row and not company_name:
                    company_name = current_row['Company_Name']
            
            # Calculate changes
            weight_change = current_weight - prev_weight  # Note: positive means weight increased
            position_change = current_position - prev_position  # Note: positive means position increased
            
            # Decompose weight change
            # Weight change due to position change (active rebalancing)
            if prev_total_market_value > 0 and prev_price > 0:
                # Position increase contributes positively to weight
                weight_change_from_position = (position_change * prev_price) / prev_total_market_value
            else:
                weight_change_from_position = 0
            
            # Weight change due to price change
            if prev_total_market_value > 0 and prev_position > 0:
                # Price increase contributes positively to weight
                price_change = current_price - prev_price
                weight_change_from_price = (price_change * prev_position) / prev_total_market_value
            else:
                weight_change_from_price = 0
            
            # Only include if there's meaningful data
            if prev_weight > 0 or current_weight > 0:
                results.append({
                    'Date': current_date.strftime('%m/%d/%Y'),
                    'Ticker': ticker,
                    'Company_Name': company_name,
                    'Prev_Weight': prev_weight,
                    'Current_Weight': current_weight,
                    'Weight_Change': weight_change,
                    'Prev_Position': prev_position,
                    'Current_Position': current_position,
                    'Position_Change': position_change,
                    'Prev_Price': prev_price,
                    'Current_Price': current_price,
                    'Price_Change': current_price - prev_price if prev_price > 0 else 0,
                    'Weight_Change_from_Position': weight_change_from_position,
                    'Weight_Change_from_Price': weight_change_from_price,
                    'Residual': weight_change - weight_change_from_position - weight_change_from_price
                })
    
    return pd.DataFrame(results)


def create_daily_weight_change_summary(weight_changes_df):
    """
    Create a daily summary of weight changes.
    
    Parameters:
    -----------
    weight_changes_df : pd.DataFrame
        DataFrame from calculate_weight_changes
        
    Returns:
    --------
    pd.DataFrame
        Summary DataFrame with daily aggregated metrics
    """
    if weight_changes_df.empty:
        return pd.DataFrame()
    
    daily_summary = []
    
    for date in weight_changes_df['Date'].unique():
        date_data = weight_changes_df[weight_changes_df['Date'] == date]
        
        # Get stocks with significant changes
        significant_weight_increases = date_data[date_data['Weight_Change'] > 0.001].nlargest(3, 'Weight_Change')
        significant_weight_decreases = date_data[date_data['Weight_Change'] < -0.001].nsmallest(3, 'Weight_Change')
        
        # Calculate aggregates
        total_position_impact = date_data['Weight_Change_from_Position'].abs().sum()
        total_price_impact = date_data['Weight_Change_from_Price'].abs().sum()
        
        daily_summary.append({
            'Date': date,
            'Stocks_with_Changes': len(date_data[date_data['Weight_Change'].abs() > 0.0001]),
            'Total_Position_Impact': total_position_impact,
            'Total_Price_Impact': total_price_impact,
            'Top_Weight_Increases': ', '.join([f"{row['Ticker']} (+{row['Weight_Change']:.4f})" 
                                              for _, row in significant_weight_increases.iterrows()]),
            'Top_Weight_Decreases': ', '.join([f"{row['Ticker']} ({row['Weight_Change']:.4f})" 
                                              for _, row in significant_weight_decreases.iterrows()]),
            'Stocks_Added': len(date_data[date_data['Prev_Weight'] == 0]),
            'Stocks_Removed': len(date_data[date_data['Current_Weight'] == 0])
        })
    
    return pd.DataFrame(daily_summary)