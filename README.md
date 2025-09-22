# ARK ETF Portfolio Concentration Analysis

This project analyzes the concentration of ARK ETF portfolios using the Herfindahl-Hirschman Index (HHI) and tracks portfolio changes over time.

## Features

### 1. HHI Concentration Analysis
- Calculates HHI as the sum of squared portfolio weights
- HHI = Σ(weight²) where weights are in decimal format (0.056 for 5.6%)
- All HHI values guaranteed to be < 1 (validated across all ETFs)
- Tracks effective number of stocks (1/HHI)

### 2. Portfolio Changes Tracking
- Identifies when stocks are added or removed from portfolios
- Tracks changes on a daily basis
- Generates detailed Excel reports with:
  - Summary statistics
  - Daily changes log
  - Addition/removal matrices
  - Complete change history

### 3. Return Contribution Analysis
- P&L-based contribution calculations
- Separate analysis for positive and negative contributors
- Top performer concentration metrics
- Pie chart visualizations

### 4. Multi-ETF Support
- Supports all ARK ETFs: ARKK, ARKW, ARKQ, ARKF, ARKG
- Configurable time periods for analysis
- Batch processing capabilities

## Project Structure

```
code/
├── main.py                 # Main entry point with configuration
├── data_loader.py          # Data loading and preprocessing
├── metrics.py              # HHI and contribution calculations
├── returns.py              # Returns calculations (daily/weekly)
├── portfolio_changes.py   # Stock addition/removal tracking
├── plots.py                # Visualization functions
├── export.py               # Excel export functionality
└── output/                 # Generated files (Excel, PNG)
```

## Configuration

Edit the configuration section in `main.py`:

```python
# ETFs to analyze
ETFS_TO_ANALYZE = ['ARKK', 'ARKW', 'ARKQ', 'ARKF', 'ARKG']

# Analysis period
CUSTOM_PERIOD = {
    'start': '2024-04-01',  # or None for earliest
    'end': '2024-08-31'     # or None for latest
}
```

## Running the Analysis

```bash
python main.py
```

## Output Files

All output files are saved in the `output/` directory:

### For each ETF:
- `[ETF]_Concentration_Analysis.xlsx` - Complete HHI and returns analysis
- `[ETF]_Portfolio_Changes_[date].xlsx` - Stock addition/removal tracking
- `[ETF]_Analysis_Before_2025.png` - Historical analysis charts
- `[ETF]_Analysis_2025.png` - 2025 analysis charts (if applicable)
- `[ETF]_Custom_Period_Pie_Charts.png` - P&L contribution pie charts

### Excel Sheets Include:
- **HHI Analysis**: Daily HHI values and holdings count
- **Daily Returns**: Day-by-day return calculations
- **Weekly Returns**: Week-by-week aggregated returns
- **Portfolio Changes**: Detailed tracking of stock additions/removals
- **P&L Contributions**: Top contributors and their impact

## Key Metrics

### HHI Interpretation:
- HHI < 0.01: Highly diversified
- HHI 0.01-0.15: Moderately concentrated
- HHI 0.15-0.25: Concentrated
- HHI > 0.25: Highly concentrated

### Typical Values (as of Aug 2024):
- ARKK: HHI ≈ 0.054 (18-19 effective stocks)
- ARKW: HHI ≈ 0.052 (19-20 effective stocks)
- ARKQ: HHI ≈ 0.056 (17-18 effective stocks)
- ARKF: HHI ≈ 0.048 (20-21 effective stocks)
- ARKG: HHI ≈ 0.040 (25 effective stocks)

## Data Requirements

Place historical data files in the parent directory:
- `ARKK_historical data_*.xlsx`
- `ARKW_historical data_*.xlsx`
- `ARKQ_historical data_*.xlsx`
- `ARKF_historical data_*.xlsx`
- `ARKG_historical data_*.xlsx`

Required columns:
- Date
- Bloomberg Name
- Ticker
- Position
- Stock_Price
- Weight

## Notes

- Cash funds (XX, MVRXX, DGCXX, FEDXX) are automatically excluded
- Weights > 1 are automatically converted to decimals (÷100)
- All analyses use daily frequency by default
- Stock splits/dividends should be pre-adjusted in source data