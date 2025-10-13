# ARK ETF Portfolio Concentration Analysis

Jupyter notebook for analyzing ARK Invest ETF portfolio concentration using HHI (Herfindahl-Hirschman Index) and tracking frequent drivers of daily P&L.

## Features

- **HHI Concentration**: Daily portfolio concentration tracking (HHI = Σ(weight²))
- **ENH Metric**: Effective Number of Holdings (ENH = 1/HHI)
- **P&L Attribution**: Identifies stocks contributing to 50% of daily profits/losses
- **Visual Analytics**: Time series charts and frequency analysis
- **Multi-ETF**: Supports all ARK ETFs (ARKK, ARKW, ARKQ, ARKF, ARKG, ARKX)

## Project Structure

```
├── input/                  # ETF data files
├── code/ARK_ETF_Analysis.ipynb  # Main notebook
└── output/                 # Results (Excel + PNG charts)
```

## Quick Start

```bash
cd code
jupyter notebook ARK_ETF_Analysis.ipynb
```

Edit cell-3 to configure date range, then run all cells.

## 📈 Output Files

Analysis results are saved in the `output/` directory:

### Per ETF Output
1. **Excel File**: `[ETF]_Analysis_YYYYMMDD.xlsx`
   - Sheet: Daily_HHI_Analysis
   - Columns: Date, HHI, ENH, Holdings_Count, Top_50pct_Profit_Count, Top_50pct_Profit_Tickers, Top_50pct_Loss_Count, Top_50pct_Loss_Tickers

2. **Visualization Charts** (PNG):
   - `[ETF]_HHI_ENH_TimeSeries.png` - Dual chart showing HHI and ENH over time
   - `[ETF]_Frequent_Drivers_50pct_Profits.png`
   - `[ETF]_Frequent_Drivers_50pct_Losses.png`

## 📊 Key Metrics

### HHI Interpretation
| HHI Range | Concentration Level | Effective Stocks |
|-----------|-------------------|------------------|
| < 0.01 | Highly Diversified | > 100 |
| 0.01-0.15 | Moderately Concentrated | 7-100 |
| 0.15-0.25 | Concentrated | 4-7 |
| > 0.25 | Highly Concentrated | < 4 |

### Typical ARK ETF Values (2024)
| ETF | Average HHI | Effective Stocks |
|-----|-------------|------------------|
| ARKK | ~0.054 | 18-19 |
| ARKW | ~0.052 | 19-20 |
| ARKQ | ~0.056 | 17-18 |
| ARKF | ~0.048 | 20-21 |
| ARKG | ~0.040 | 25 |
| ARKX | ~0.065 | 15-16 |

## 📋 Requirements

### Data Format
Place ETF data files in `input/` folder:
- Format: `[ETF]_Transformed_Data.xlsx`
- Read from: Sheet1
- Required columns:
  - Date
  - Bloomberg Name
  - Ticker
  - Position
  - Stock_Price
  - Weight

### Python Dependencies
```bash
pip install pandas numpy openpyxl matplotlib seaborn jupyter
```

## 🔍 Analysis Details

### Step 1: Load All ETF Data
- Loads data from `input/[ETF]_Transformed_Data.xlsx`
- Converts weights to decimal format if needed
- Filters out cash positions (XX, MVRXX, DGCXX, FEDXX)
- Applies selected date range filter

### Step 2: Calculate HHI and ENH
- **HHI Formula**: Sum of squared portfolio weights (HHI = Σ(weight²))
- **ENH Formula**: Effective Number of Holdings (ENH = 1/HHI)
- Calculates both metrics for each day across all ETFs
- Tracks holdings count (number of non-cash positions)

### Step 3: Calculate P&L and Top Contributors
- **Adjusted P&L**: Accounts for position changes and inflows/outflows
- Identifies stocks contributing to 50% of daily profits
- Identifies stocks contributing to 50% of daily losses
- Saves results to Excel files

### Step 4: Generate Visualizations
- HHI/ENH dual time series chart with concentration thresholds
- Frequency charts showing most common profit drivers (with gradient colors)
- Frequency charts showing most common loss drivers (with gradient colors)

## 📝 Notes

- Cash positions (XX, MVRXX, DGCXX, FEDXX) are automatically excluded
- Weights > 1 are automatically converted to decimal format
- Analysis uses daily frequency for all calculations
- P&L calculations start from the second day (need previous day for comparison)

## 📧 Contact

For questions or issues, please open an issue on GitHub.