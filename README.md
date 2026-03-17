# Cloud Service Providers: Data Cleaning & Transformation Pipeline

A comprehensive, production-grade automated pipeline for processing multi-cloud usage and billing data (AWS, Azure, GCP). Designed specifically to power FinOps, SRE KPIs, and interactive analytics.

## Project Overview

Raw cloud billing data is famously dirty, containing missing fields, incorrect formats, PII leakage, timezone skews, and unmatched IDs. This project builds a reliable two-stage data pipeline consisting of a **Cleaning Layer** and a **Transformation Layer** to turn highly-corrupted raw cloud logs into analytics-ready data assets.

## Project Structure
```text
pro1/
├── data/
│   ├── raw/                 # Synthetically generated dirty data across 7 tables
│   ├── cleaned/             # The output of Phase 3 (cleaned_usage_billing.csv)
│   └── transforms/          # The output of Phase 4 transformation outputs (T01-T20)
├── docs/
│   └── dataset_schema.md    # Full documentation of the raw dataset relationships
├── scenarios/               # S01-S20: Data cleaning python modules
├── validations/             # V01-V20: Pytest assertion files for each scenario
├── transforms/              # T01-T20: Transformation and business logic modules
├── tests/
│   ├── conftest.py          # Pytest configuration and shared fixtures
│   └── test_cleaning_suite.py # Automated testing suite validating the cleaning layer
├── cleaning_notebook.ipynb  # Interactive execution and validation of S01-S20
└── transform_notebook.ipynb # Interactive execution and graphing for T01-T20
```

## Phase 1 & 2: Dataset Generation
We designed 7 interactive tables to simulate a corporate cloud environment:
1. `usage_billing.csv` (10,000 rows - core table)
2. `account_master.csv`
3. `sku_catalog.csv`
4. `resource_inventory.csv`
5. `support_tickets.csv`
6. `incidents.csv`
7. `log_events.csv`

## Phase 3: The Cleaning Layer (S01-S20)
We implemented 20 distinct data cleaning algorithms across domains to resolve issues:
*   **Normalization:** Account IDs (S01), Service/SKUs (S03), Units (S04), Cost/Currency (S05), Regions (S06)
*   **Time & Date:** Global UTC Timestamp conversion (S02), Log Time Skew correction (S20)
*   **Data Integrity:** Duplicates (S07), Anomaly Spikes (S09), Tag Compliance (S10)
*   **Relational Mapping:** Cross-referencing against Resource Inventory (S11), Price Catalogs (S14), and FX Rates (S15)
*   **Security & Compliance:** PII Masking in Support Tickets (S12)
*   **Operational Logs:** Incident Mapping (S13), Utilization formatting (S16), SLA parsing (S19)

**Automated Testing:** We wrote comprehensive `pytest` functions in `test_cleaning_suite.py` asserting that every single scenario correctly cleans the anomalies injected.

## Phase 4: The Transformation Layer (T01-T20)
We built 20 modular Python scripts that ingest the clean data and produce aggregated datasets, answering key business questions:
*   **FinOps:** Chargeback cubes (T02), RI/SP Utilization (T03), Idle Resource Savings (T04, T13), FinOps KPIs (T12)
*   **SRE:** SLA Attainment (T05), Incident MTTR (T06), Ticket Clustering (T15), Security Event Correlations (T19)
*   **Analytics:** Cost Forecasting (T10), Unit Economics (T17), Multi-Cloud Consolidation (T18)

## Phase 5 (Notebooks): Interactive Execution
Using Jupyter Notebooks, we provide a step-by-step interactive interface:
*   `cleaning_notebook.ipynb`: Imports S01-S20 sequentially, viewing the transformations live.
*   `transform_notebook.ipynb`: Imports T01-T20 sequentially and attaches complex data visualizations (Timeseries plots, Bar Charts, Pie charts) directly beneath the logic execution.

## How it Works & Execution Flow

This project is built to execute in a strict, sequential pipeline. To run the project from scratch, follow these exact steps:

### Step 1: Virtual Environment Setup
Ensure your python virtual environment is active containing dependencies like `pandas`, `pytest`, `seaborn`, and `jupyter`.
```bash
source venv/bin/activate
# Or natively install: pip install pandas pytest matplotlib seaborn notebook
```

### Step 2: Generate the Synthetic Data
This script dynamically creates the 7 raw CSV tables and injects the PDF-defined anomalies.
```bash
python generate_dataset.py
```
*Outputs: 7 dirty CSV files in `data/raw/`*

### Step 3: Run the Test Suite (Validation)
Before transforming, we run our unit tests to ensure the cleaning logic (S01-S20) correctly catches and resolves the injected garbage data.
```bash
pytest tests/test_cleaning_suite.py -v
```
*Outputs: Validation metrics asserting 100% test coverage.*

### Step 4: The Cleaning Notebook (Interactive S01-S20)
Instead of a black-box script, execute the cleaning notebook. It imports each scenario step-by-step, loads the raw data, applies the cleaning, and outputs the final structured `cleaned_usage_billing.csv`.
```bash
jupyter notebook cleaning_notebook.ipynb
```
*Action: Run all cells in the notebook.*
*Outputs: `data/cleaned/cleaned_usage_billing.csv`*

### Step 5: The Transformation Notebook (Interactive T01-T20)
Once the data is cleaned, execute the transformation notebook. It loads the clean dataset, applies business logic transformations modularly, and renders critical visualizations directly inline.
```bash
# Optional: To auto-generate the notebook programmatically up to the current progress
python transform_notebook_init.py

# Launch the visualizer
jupyter notebook transform_notebook.ipynb
```
*Action: Run all cells to view the T01-T20 outputs alongside their charts.*
