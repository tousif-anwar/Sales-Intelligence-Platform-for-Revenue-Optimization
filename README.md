# Sales Intelligence Platform for Revenue Optimization

This platform ingests raw sales data, cleans and transforms it, and visualizes KPIs to help sales leaders identify revenue leaks, top reps, ideal customer profiles, and churn risks.

## Project Structure

```
project/
├── data/
│   ├── raw/             # Raw data from CRM exports or mock data
│   └── processed/       # Cleaned and transformed data
├── src/
│   ├── generate_mock_data.py  # Generate mock sales data
│   ├── etl_pipeline.py        # Data cleaning and transformation
│   ├── churn_model.py         # ML model for churn prediction
│   └── run_pipeline.py        # Main script to run the entire pipeline
├── models/              # Saved ML models
├── notebooks/           # Jupyter notebooks for exploratory analysis
└── dashboard/           # BI dashboard exports and visualizations
```

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (install using `pip install -r requirements.txt`)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Pipeline

To run the complete pipeline:

```
python src/run_pipeline.py
```

This will:
1. Generate mock sales data
2. Clean and transform the data
3. Create analytics-ready datasets
4. Build a churn prediction model
5. Export visualization files for dashboards

## Features

### Data Ingestion
- Import CSV exports from Salesforce, HubSpot, or use mock data
- Includes fields like lead source, contact dates, rep name, stage, deal size, close date

### Data Pipeline
- ETL process with Python + Pandas
- Data cleaning (nulls, duplicates, malformed text)
- Date/time normalization and sales cycle duration calculation

### Sales Performance Metrics
- Win rate, average deal size, revenue per rep, conversion rates per stage
- Churn prediction using logistic regression

### BI Dashboard Data
- Sales pipeline funnel
- Rep performance comparison
- Monthly revenue trends
- Lead conversion by source
- Customer churn risk analysis

## Dashboard Integration

The exported files in the `dashboard/` directory can be imported into:

- **Power BI**: Use the .xlsx files for direct import
- **Tableau**: Use the .csv files for data source connections

## Customization

### Using Your Own CRM Data
Replace the mock data generation step by placing your exported CRM data in the `data/raw/` directory as a CSV file named `sales_data.csv`.

### Modifying the ETL Process
Edit the `etl_pipeline.py` file to adjust the data cleaning and transformation steps to match your specific data structure.

### Changing the Churn Model
The churn prediction model can be customized in `churn_model.py`. By default, it uses logistic regression, but you can switch to random forest by changing the model_type parameter.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## SaaS Product Usage & Revenue Analytics

The script `src/saas_bi_pipeline.py` simulates a SaaS business by generating mock customer, usage, and revenue data. It builds a star schema with fact tables for usage and revenue and dimensions for customers, plans, and time.

### Usage

1. Run the pipeline:
   ```bash
   python src/saas_bi_pipeline.py
   ```
   This creates CSV files under `data/processed/` that can be loaded into BI tools.
2. Connect the processed data to **Looker Studio** or **Power BI** and create persona-based dashboards:
   - **CEO**: Growth metrics and churn rate
   - **CPO**: Feature usage and adoption trends
   - **CFO**: MRR/ARR and revenue forecasts

### KPIs
The pipeline calculates key metrics including churn rate, DAU/MAU, expansion revenue, LTV:CAC ratio, and feature adoption trends. Results are saved to `data/processed/kpis.json` for quick reference.

See `INSIGHTS.md` for example strategic takeaways derived from the metrics.
