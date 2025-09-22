"""
Metrics calculation module for portfolio analysis.
Handles HHI and contribution calculations.
"""

import pandas as pd
import numpy as np


def calculate_holdings_hhi(holdings_data):
    """
    Calculate HHI based on portfolio weights.
    HHI = sum of squared weights (as decimals)
    
    Parameters:
    -----------
    holdings_data : pd.DataFrame
        Holdings data with Weight column
        
    Returns:
    --------
    float
        HHI value
    """
    # Filter out cash funds
    cash_funds = ['XX', 'MVRXX', 'DGCXX', 'FEDXX']
    filtered_data = holdings_data[~holdings_data['Ticker'].isin(cash_funds)]
    
    if len(filtered_data) == 0:
        return 0.0
    
    # Get weights (already converted to decimal in data_loader)
    # Weight column should already be in decimal format (0.056 for 5.6%)
    weights = filtered_data['Weight'].values
    
    # Calculate HHI as sum of squared weights
    # No normalization - use weights as they are
    hhi = np.sum(weights ** 2)
    
    return hhi


def calculate_portfolio_contributions(returns, weights, pnl_data=None):
    """
    Calculate portfolio contribution metrics based on P&L (NOT HHI).
    
    Parameters:
    -----------
    returns : dict
        Dictionary of stock returns
    weights : dict
        Dictionary of stock weights  
    pnl_data : dict
        P&L data for each stock
        
    Returns:
    --------
    dict
        Dictionary with contribution metrics (no HHI here)
    """
    if not pnl_data or len(pnl_data) == 0:
        return None
    
    # Calculate total P&L
    total_pnl = sum(stock_data['pnl'] for stock_data in pnl_data.values())
    
    if total_pnl == 0:
        return None
    
    # Calculate P&L contributions
    pnl_contributions = {}
    for ticker, stock_data in pnl_data.items():
        pnl_contributions[ticker] = stock_data['pnl'] / abs(total_pnl)
    
    # Sort by absolute contribution
    sorted_contributions = sorted(pnl_contributions.items(), 
                                 key=lambda x: abs(x[1]), 
                                 reverse=True)
    
    # Calculate top N shares
    abs_contributions = [abs(c[1]) for c in sorted_contributions]
    top_1_share = abs_contributions[0] if len(abs_contributions) >= 1 else 0
    top_3_share = sum(abs_contributions[:3]) if len(abs_contributions) >= 3 else sum(abs_contributions)
    top_5_share = sum(abs_contributions[:5]) if len(abs_contributions) >= 5 else sum(abs_contributions)
    top_10_share = sum(abs_contributions[:10]) if len(abs_contributions) >= 10 else sum(abs_contributions)
    
    # Separate positive and negative contributors
    positive_contributors = [(t, c) for t, c in pnl_contributions.items() if c > 0]
    negative_contributors = [(t, c) for t, c in pnl_contributions.items() if c < 0]
    
    # Sort by contribution magnitude
    positive_contributors.sort(key=lambda x: x[1], reverse=True)
    negative_contributors.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Calculate positive/negative metrics
    positive_contributions = [c[1] for c in positive_contributors]
    negative_contributions = [abs(c[1]) for c in negative_contributors]
    
    total_positive = sum(positive_contributions)
    total_negative = sum(negative_contributions)
    
    # Top N positive share (as percentage of total positive)
    if total_positive > 0:
        top_1_positive_share = positive_contributions[0] / total_positive if len(positive_contributions) >= 1 else 0
        top_5_positive_share = sum(positive_contributions[:5]) / total_positive if len(positive_contributions) >= 5 else 1
        top_10_positive_share = sum(positive_contributions[:10]) / total_positive if len(positive_contributions) >= 10 else 1
    else:
        top_1_positive_share = top_5_positive_share = top_10_positive_share = 0
    
    # Top N negative share (as percentage of total negative)
    if total_negative > 0:
        top_1_negative_share = negative_contributions[0] / total_negative if len(negative_contributions) >= 1 else 0
        top_5_negative_share = sum(negative_contributions[:5]) / total_negative if len(negative_contributions) >= 5 else 1
        top_10_negative_share = sum(negative_contributions[:10]) / total_negative if len(negative_contributions) >= 10 else 1
    else:
        top_1_negative_share = top_5_negative_share = top_10_negative_share = 0
    
    return {
        'top_1_share': top_1_share,
        'top_3_share': top_3_share,
        'top_5_share': top_5_share,
        'top_10_share': top_10_share,
        'positive_contributors_count': len(positive_contributors),
        'negative_contributors_count': len(negative_contributors),
        'top_1_positive_share': top_1_positive_share,
        'top_5_positive_share': top_5_positive_share,
        'top_10_positive_share': top_10_positive_share,
        'top_1_negative_share': top_1_negative_share,
        'top_5_negative_share': top_5_negative_share,
        'top_10_negative_share': top_10_negative_share
    }


def calculate_pnl_for_period(holdings_start, holdings_end):
    """
    Calculate P&L for each stock in the period.
    
    Parameters:
    -----------
    holdings_start : pd.DataFrame
        Holdings at start of period
    holdings_end : pd.DataFrame
        Holdings at end of period
        
    Returns:
    --------
    dict
        Dictionary with P&L data for each stock
    """
    pnl_data = {}
    
    # Get unique tickers from both periods
    all_tickers = set(holdings_start['Ticker'].unique()) | set(holdings_end['Ticker'].unique())
    
    for ticker in all_tickers:
        # Skip cash funds
        if isinstance(ticker, str) and ticker in ['XX', 'MVRXX', 'DGCXX', 'FEDXX']:
            continue
        
        start_rows = holdings_start[holdings_start['Ticker'] == ticker]
        end_rows = holdings_end[holdings_end['Ticker'] == ticker]
        
        if len(start_rows) > 0 and len(end_rows) > 0:
            start_row = start_rows.iloc[0]
            end_row = end_rows.iloc[0]
            
            # Calculate P&L using start position
            # P&L = (start_position * end_price) - (start_position * start_price)
            # This is equivalent to: start_position * (end_price - start_price)
            start_position = start_row['Position']
            start_price = start_row['Stock_Price']
            end_price = end_row['Stock_Price']
            
            pnl = start_position * (end_price - start_price)
            
            pnl_data[ticker] = {
                'pnl': pnl,
                'start_price': start_price,
                'end_price': end_price,
                'start_position': start_position,
                'end_position': end_row['Position'],
                'weight': end_row['Weight']
            }
    
    return pnl_data