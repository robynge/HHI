# ARK ETF Portfolio Concentration Analysis

A comprehensive analysis system for tracking ARK Invest ETF portfolio concentration using the Herfindahl-Hirschman Index (HHI), portfolio changes, and weight dynamics.

## 📊 Features

### 1. HHI Concentration Analysis
- Calculates Herfindahl-Hirschman Index for portfolio concentration measurement
- HHI = Σ(weight²) where weights are in decimal format
- Tracks effective number of stocks (1/HHI)
- Daily tracking of concentration changes

### 2. Portfolio Changes Tracking
- Daily monitoring of stock additions and removals
- Comprehensive change history logging
- Weight change analysis for existing holdings

### 3. P&L Contribution Analysis
- Identifies top profit contributors (stocks contributing to 50% of positive P&L)
- Daily tracking of profit concentration
- Performance attribution analysis

### 4. Multi-ETF Support
- Supports all ARK ETFs: ARKK, ARKW, ARKQ, ARKF, ARKG, ARKX
- Batch processing for multiple ETFs
- Configurable analysis periods

## 📁 Project Structure

```
HHI/
├── input/                  # ETF data files (Excel format)
│   ├── ARKK_Transformed_Data.xlsx
│   ├── ARKW_Transformed_Data.xlsx
│   └── ...
├── code/                   # Source code
│   ├── main.py            # Main entry point
│   ├── data_loader.py     # Data loading from input folder
│   ├── metrics.py         # HHI and P&L calculations
│   ├── portfolio_changes.py  # Track stock additions/removals
│   └── weight_changes.py  # Weight change analysis
├── output/                 # Analysis results (Excel files)
└── reports/               # Documentation and reports
```

## ⚙️ Configuration

Edit `code/main.py` to configure:

```python
# ETFs to analyze
ETFS_TO_ANALYZE = ['ARKK', 'ARKW', 'ARKQ', 'ARKF', 'ARKG', 'ARKX']

# Analysis period
ANALYSIS_PERIOD = {
    'start': '2024-04-01',
    'end': datetime.now().strftime('%Y-%m-%d')  # Today
}
```

## 🚀 Quick Start

```bash
# Run the analysis
cd code
python main.py
```

## 📈 Output Files

Analysis results are saved in the `output/` directory:

### Excel Files (per ETF)
- `[ETF]_Analysis_YYYYMMDD.xlsx` containing:
  - **Daily_HHI_Analysis**: HHI values, holdings count, top profit contributors
  - **Portfolio_Changes**: Stock additions and removals
  - **Weight_Changes**: Daily weight changes for all holdings

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
pip install pandas numpy openpyxl
```

## 🔍 Analysis Details

### Daily Tracking
- **HHI Calculation**: Sum of squared portfolio weights
- **Holdings Count**: Number of non-cash positions
- **Top Contributors**: Stocks contributing to 50% of daily positive P&L

### Portfolio Changes
- Tracks when stocks enter or exit the portfolio
- Records daily weight changes for all holdings
- Identifies significant portfolio rebalancing events

## 📝 Notes

- Cash positions (XX, MVRXX, DGCXX, FEDXX) are automatically excluded
- Weights > 1 are automatically converted to decimal format
- Analysis uses daily frequency for all calculations
- P&L calculations start from the second day (need previous day for comparison)

## 📧 Contact

For questions or issues, please open an issue on GitHub.