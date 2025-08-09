import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

# Directory paths
RAW_DIR = os.path.join('data', 'raw')
PROCESSED_DIR = os.path.join('data', 'processed')

# Ensure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ---------------------------
# Data Generation
# ---------------------------

# Plans definition
dim_plan = pd.DataFrame({
    'plan_id': [1, 2, 3],
    'plan_name': ['Basic', 'Pro', 'Enterprise'],
    'monthly_fee': [50, 100, 250]
})

# Generate customers
n_customers = 200
start_date = datetime.now() - timedelta(days=365)
customer_ids = range(1, n_customers + 1)

customers = []
for cid in customer_ids:
    signup = start_date + timedelta(days=np.random.randint(0, 365))
    plan = np.random.choice(dim_plan['plan_id'])
    cancel_date = None
    upgrade_date = None
    current_plan = plan

    # Randomly decide cancellation
    if np.random.rand() < 0.1:  # 10% churn
        cancel_date = signup + timedelta(days=np.random.randint(30, 365))
        if cancel_date > datetime.now():
            cancel_date = None

    # Randomly decide upgrade
    if cancel_date is None and np.random.rand() < 0.2:
        upgrade_date = signup + timedelta(days=np.random.randint(30, 300))
        if upgrade_date < datetime.now():
            higher_plans = [p for p in dim_plan['plan_id'] if p > plan]
            if higher_plans:
                current_plan = np.random.choice(higher_plans)
        else:
            upgrade_date = None

    cac = np.random.uniform(100, 500)

    customers.append({
        'customer_id': cid,
        'signup_date': signup.date(),
        'plan_id': plan,
        'current_plan_id': current_plan,
        'cancel_date': cancel_date.date() if cancel_date else None,
        'upgrade_date': upgrade_date.date() if upgrade_date else None,
        'cac': cac
    })

customers_df = pd.DataFrame(customers)
customers_df.to_csv(os.path.join(RAW_DIR, 'customers.csv'), index=False)

# Generate usage logs for last 90 days
features = ['analytics', 'collaboration', 'reporting', 'notifications', 'mobile']
end_date = datetime.now().date()
start_usage_date = end_date - timedelta(days=89)

dates = pd.date_range(start_usage_date, end_date, freq='D')

usage_records = []
for date in dates:
    active_customers = customers_df[(customers_df['signup_date'] <= date) &
                                    (customers_df['cancel_date'].isna() | (customers_df['cancel_date'] > date))]
    for cid in active_customers['customer_id']:
        # Probability of login
        if np.random.rand() < 0.6:  # 60% chance to log in
            # number of features used between 1 and 3
            used_features = np.random.choice(features, size=np.random.randint(1, 4), replace=False)
            for feat in used_features:
                usage_records.append({'date': date, 'customer_id': cid, 'feature': feat, 'usage_count': 1})

usage_df = pd.DataFrame(usage_records)
usage_df.to_csv(os.path.join(RAW_DIR, 'usage_logs.csv'), index=False)

# Generate revenue records (monthly)
revenue_records = []
for _, row in customers_df.iterrows():
    signup = pd.to_datetime(row['signup_date'])
    cancel = pd.to_datetime(row['cancel_date']) if pd.notnull(row['cancel_date']) else end_date
    plan_id = row['plan_id']
    current_plan_id = row['current_plan_id']
    upgrade = pd.to_datetime(row['upgrade_date']) if pd.notnull(row['upgrade_date']) else None

    current_date = signup
    while current_date <= cancel:
        plan_to_use = plan_id
        if upgrade is not None and current_date >= upgrade:
            plan_to_use = current_plan_id
        fee = dim_plan.loc[dim_plan['plan_id'] == plan_to_use, 'monthly_fee'].iloc[0]
        revenue_records.append({
            'date': current_date.replace(day=1),
            'customer_id': row['customer_id'],
            'mrr': fee,
            'arr': fee * 12
        })
        current_date += pd.DateOffset(months=1)

revenue_df = pd.DataFrame(revenue_records)
revenue_df.to_csv(os.path.join(RAW_DIR, 'revenue.csv'), index=False)

# ---------------------------
# Build Star Schema
# ---------------------------

# Dimension tables
dim_customer = customers_df[['customer_id', 'signup_date', 'plan_id', 'current_plan_id', 'cancel_date', 'upgrade_date', 'cac']]
dim_time = pd.DataFrame({'date': dates})
dim_time['day'] = dim_time['date'].dt.day
ndays = dim_time['date'].dt.isocalendar()
dim_time['week'] = ndays.week
dim_time['month'] = dim_time['date'].dt.month
dim_time['year'] = dim_time['date'].dt.year

# Save dimension tables
dim_customer.to_csv(os.path.join(PROCESSED_DIR, 'dim_customer.csv'), index=False)
dim_plan.to_csv(os.path.join(PROCESSED_DIR, 'dim_plan.csv'), index=False)
dim_time.to_csv(os.path.join(PROCESSED_DIR, 'dim_time.csv'), index=False)

# Fact tables
fact_usage = usage_df.copy()
fact_usage.to_csv(os.path.join(PROCESSED_DIR, 'fact_usage.csv'), index=False)

fact_revenue = revenue_df.copy()
fact_revenue.to_csv(os.path.join(PROCESSED_DIR, 'fact_revenue.csv'), index=False)

# ---------------------------
# KPI Calculations
# ---------------------------

# Churn rate
churn_rate = customers_df['cancel_date'].notna().mean()

# DAU and MAU
daily_active = usage_df.groupby('date')['customer_id'].nunique()
dau = daily_active.mean()

usage_df['month'] = pd.to_datetime(usage_df['date']).dt.to_period('M')
monthly_active = usage_df.groupby('month')['customer_id'].nunique()
mau = monthly_active.mean()

# Expansion revenue
expansion_revenue = 0
for _, row in customers_df.dropna(subset=['upgrade_date']).iterrows():
    old_fee = dim_plan.loc[dim_plan['plan_id'] == row['plan_id'], 'monthly_fee'].iloc[0]
    new_fee = dim_plan.loc[dim_plan['plan_id'] == row['current_plan_id'], 'monthly_fee'].iloc[0]
    upgrade_date = pd.to_datetime(row['upgrade_date'])
    months_after_upgrade = max(0, (end_date - upgrade_date.date()).days // 30)
    expansion_revenue += (new_fee - old_fee) * months_after_upgrade

# LTV:CAC ratio
revenue_per_customer = revenue_df.groupby('customer_id')['mrr'].sum()
ltv = revenue_per_customer.mean()
average_cac = customers_df['cac'].mean()
ltv_cac_ratio = ltv / average_cac

# Feature adoption trends
feature_trends = usage_df.copy()
feature_trends['month'] = feature_trends['month'].astype(str)
feature_trends = feature_trends.groupby(['month', 'feature'])['usage_count'].sum().unstack(fill_value=0)
feature_trends.to_csv(os.path.join(PROCESSED_DIR, 'feature_adoption_trends.csv'))

# Save KPIs to a JSON file
kpis = {
    'churn_rate': churn_rate,
    'average_dau': dau,
    'average_mau': mau,
    'expansion_revenue': expansion_revenue,
    'ltv_cac_ratio': ltv_cac_ratio
}

pd.Series(kpis).to_json(os.path.join(PROCESSED_DIR, 'kpis.json'))

# Print KPI summary
print('KPI Summary')
print('-----------')
print(f"Churn rate: {churn_rate:.2%}")
print(f"Average DAU: {dau:.2f}")
print(f"Average MAU: {mau:.2f}")
print(f"Expansion revenue: ${expansion_revenue:,.2f}")
print(f"LTV:CAC ratio: {ltv_cac_ratio:.2f}")
print('\nFeature adoption trends (last 5 months):')
print(feature_trends.tail())
