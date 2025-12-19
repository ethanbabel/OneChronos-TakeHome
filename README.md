## Overview
This repository contains my work for the OneChronos analytics take-home challenge.
The goal is to (1) build a merged trade + NBBO dataset using an as-of join and
(2) explore market microstructure behavior across four symbols using quotes and
trades data. I focused on clean, reproducible preprocessing, and then created
notebook-based analyses for quotes, trades, and a simple predictive baseline on
NVDA trades.

## Usage
1. Create and activate virtual environment:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
2. Install dependencies:
    - `pip install -r requirements.txt`
3. Create the merged dataset:
   - `python scripts/construct_merged.py`
   - Output: `data/merged_trade_quote_2024_04_01.csv`
4. Exploratory analysis:
   - `research/research.ipynb` for quote-based metrics and time series plots.
5. Classification baseline:
   - `research/NVDA_classifier.ipynb` for trades-only models on NVDA.

## Data
Inputs:
- `data/quote_data_2024_04_01.csv`: NBBO snapshots (timestamp, symbol_id, bid/ask, sizes).
- `data/trade_data_2024_04_01.csv`: Trades (timestamp, symbol_id, exchange code, price, size).

Important: The dataset is very small (only ~100 trade observations total, with
~90 of them in NVDA). This limits the reliability of any statistical or ML
conclusions and makes model accuracy highly sensitive to small changes.

## Part 1: Merged Dataset (As-Of Join)
File: `scripts/construct_merged.py`
- Reads trades and quotes as pandas DataFrames.
- Converts timestamps to datetime and sorts on the timestamp key to satisfy
  `merge_asof` requirements.
- Performs a backward as-of join by `symbol_id` to enrich each trade with the
  most recent NBBO.
- Consolidates `price_decimal` into a single column and prefixes NBBO fields
  (`NBBO_bid_price`, `NBBO_ask_price`, etc.) for clarity.

Rationale:
- An as-of join matches each trade to the prevailing quote at execution time.
- Sorting by timestamp is required by pandas and avoids misalignment errors.
- Prefixing quote columns makes the merged schema explicit.

## Part 2: Quote Analysis and Time Series
File: `research/research.ipynb`
- Adds quote-level derived fields at each timestamp:
  - `bid_px`, `ask_px`, `mid_px`, `spread`, `spread_bps`, `depth`.
- Plots time series comparisons across symbols using all available timestamps
  (no resampling), with markers for visibility when a symbol has few points.
- To handle large intraday gaps, plots use an evenly spaced “event-time” axis
  with vertical dashed lines to mark large gaps (>= 5 minutes).

Rationale:
- Keeping every timestamp preserves the true event flow.
- Event-time plotting makes clustered periods legible without hiding gaps.
- `spread_bps` allows fair cross-symbol comparison across price levels.

## Trades-Only Modeling (NVDA)
File: `research/NVDA_classifier.ipynb`
Setup:
- Builds per-symbol trade data with scaled prices and rolling volatility.
- Defines the target as next-trade direction (+1 if next return > 0, else -1).
- Uses only current-time features to avoid leakage from future data:
  - `trade_size`, `trade_px`, `locally_normalized_px`, `vol_1s`, `log_ret`.
- Evaluates with `TimeSeriesSplit` to respect temporal ordering.
- Model: Gradient Boosting classifier (tree-based nonlinear model).

Result:
- Gradient Boosting accuracy: 0.6428 (mean across time splits).
  This should be interpreted cautiously due to the tiny sample size and the
  heavy concentration of trades in a single symbol.

## Next Steps (With More Time)
- Increase sample size by adding more trading days or additional symbols.
- Engineer richer features from the merged dataset:
  - Trade aggressiveness (bid/ask/mid), effective spread, quote imbalance.
  - Include features derived from a combination of trades *and* quotes datasets. 
- Test longer horizons (next minute instead of next trade) and calibrate class
  imbalance handling.
- Use purged K-fold or rolling window validation with a time gap to reduce
  leakage from overlapping rolling statistics.
- Perform robustness checks across different time buckets and volatility
  windows.
