# European Power Market: Renewable Forecast Error & Price Pass-Through Pipeline

## Overview
An automated ETL (Extract, Transform, Load) and analytical data pipeline that queries the ENTSO-E Transparency Platform API to assess how day-ahead wind forecast errors propagate into real-time imbalance settlement price spikes in the Dutch bidding zone (`NL`).

## Research Context & Motivation
European wholesale electricity markets increasingly depend on weather-dependent wind and solar generation. In day-ahead markets, clearing prices reflect forecasted renewable supply. When weather forecasts deviate from realized meteorological conditions, the physical grid faces generation imbalances. 

This repository provides an empirical framework to test:
1. Whether renewable forecast errors ($\text{Actual} - \text{Forecast}$) cause systematic price divergence between Day-Ahead Markets (DAM) and Imbalance/Balancing Markets.
2. The extent to which unexpected supply shortfalls create acute price spikes that affect energy-intensive consumers.

## Pipeline Architecture
1. **Extract**: Pulls actual generation by fuel type, day-ahead wind and solar forecasts, day-ahead hourly clearing prices, and 15-minute imbalance settlement prices using `entsoe-py`.
2. **Transform**:
   - Aggregates offshore and onshore wind capacity.
   - Resamples 15-minute dual-pricing imbalance data to hourly weighted averages.
   - Normalizes timezones to `Europe/Brussels`.
   - Computes core metrics:
     $$\text{Wind Error}_t = \text{Actual Wind}_t - \text{Forecasted Wind}_t$$
     $$\text{Price Spread}_t = \text{Imbalance Price}_t - P_{t}^{\text{DAM}}$$
3. **Load**: Persists synchronized metrics into a local SQLite database (`energy_pipeline.db`) using structured SQL tables.
4. **Analyze**: Queries structural spread anomalies via SQL and generates visualization distributions across diurnal cycles.

## Key Empirical Finding
Supply shortfalls ($\text{Wind Error} < 0$) during high-demand ramp hours induce substantial positive balancing price spreads. During tested intervals (September 2026), an evening wind shortfall of 446.5 MW produced an imbalance price spike to €366.79/MWh (+€166.69/MWh spread above DAM clearing levels).

## Project Structure
```text
pw_mkt/
├── .gitignore          # Excludes environment tokens, databases, and caches
├── .env                # Local API credentials (not tracked)
├── requirements.txt    # Project dependencies
├── README.md           # Documentation and methodology
├── pw_mkt_API.py       # Main ETL and visualization pipeline
└── query_data.py       # SQL analysis interface for market shock detection