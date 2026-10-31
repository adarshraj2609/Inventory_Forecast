import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def run_data_analysis(df):
    print("==================================================")
    print("       RETAIL INVENTORY & DEMAND ANALYTICS        ")
    print("==================================================")
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date')
    df['Total Revenue'] = df['Units Sold'] * df['Price'] * (1 - df['Discount'] / 100)
    
    project_dir = Path(__file__).resolve().parent.parent
    output_dir = project_dir / 'outputs'
    output_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------
    # 1. KEY FINANCIAL & INVENTORY METRICS
    # ----------------------------------------------------
    total_revenue = df['Total Revenue'].sum()
    total_units_sold = df['Units Sold'].sum()
    avg_price = df['Price'].mean()

    print("\n--- Key Financial Summary ---")
    print(f"Total Revenue:      ${total_revenue:,.2f}")
    print(f"Total Units Sold:   {total_units_sold:,.0f}")
    print(f"Average Unit Price: ${avg_price:.2f}")

    # ----------------------------------------------------
    # 2. PRODUCT DEMAND ANALYSIS (Highest, Lowest, Daily Avg)
    # ----------------------------------------------------
    product_summary = df.groupby('Product ID').agg(
        Total_Demand=('Units Sold', 'sum'),
        Average_Daily_Demand=('Units Sold', 'mean'),
        Current_Inventory=('Inventory Level', 'mean'),
        Average_Forecast=('Demand Forecast', 'mean')
    ).reset_index()

    top_5_demand = product_summary.sort_values(by='Total_Demand', ascending=False).head(5)
    bottom_5_demand = product_summary.sort_values(by='Total_Demand', ascending=True).head(5)

    print("\n--- Top 5 Highest Demand Products ---")
    print(top_5_demand[['Product ID', 'Total_Demand', 'Average_Daily_Demand']].to_string(index=False))

    print("\n--- Top 5 Lowest Demand Products ---")
    print(bottom_5_demand[['Product ID', 'Total_Demand', 'Average_Daily_Demand']].to_string(index=False))

    # ----------------------------------------------------
    # 3. STOCK LEVEL & RISK ANALYSIS (Under-stocked / Over-stocked)
    # ----------------------------------------------------
    product_summary['Stock_Status'] = 'Optimal'
    product_summary.loc[product_summary['Current_Inventory'] < (product_summary['Average_Daily_Demand'] * 3), 'Stock_Status'] = 'Under-stocked'
    product_summary.loc[product_summary['Current_Inventory'] > (product_summary['Average_Daily_Demand'] * 15), 'Stock_Status'] = 'Over-stocked'

    under_stocked = product_summary[product_summary['Stock_Status'] == 'Under-stocked']
    over_stocked = product_summary[product_summary['Stock_Status'] == 'Over-stocked']

    print(f"\n--- Inventory Alert Summary ---")
    print(f"Under-stocked Products (High Risk of Stockout): {len(under_stocked)}")
    print(f"Over-stocked Products (High Holding Cost):     {len(over_stocked)}")
    
    # ----------------------------------------------------
    # 4. FORECAST ACCURACY ANALYSIS
    # ----------------------------------------------------
    df_forecast = df.dropna(subset=['Demand Forecast', 'Units Sold']).copy()
    df_forecast['MAE'] = np.abs(df_forecast['Units Sold'] - df_forecast['Demand Forecast'])
    
    mae = df_forecast['MAE'].mean()
    print(f"\n--- Baseline Forecast Performance ---")
    print(f"Mean Absolute Error (MAE): {mae:.2f} units")

    # ----------------------------------------------------
    # VISUALIZATIONS GENERATION
    # ----------------------------------------------------
    sns.set_theme(style="whitegrid")

    # Chart 1: Revenue by Category (Bar Chart)
    category_summary = df.groupby('Category')['Total Revenue'].sum().reset_index()
    plt.figure(figsize=(10, 5))
    ax=sns.barplot(data=category_summary, x='Category', y='Total Revenue', palette='Blues_d', hue='Category', legend=False)
    for container in ax.containers:ax.bar_label(container, fmt='%.2f', padding=-2)
    plt.title('Total Revenue Distribution by Product Category')
    plt.xlabel('Category')
    plt.ylabel('Total Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / '01_category_revenue.jpeg')
    plt.show()
    plt.close()
    

    # Chart 2: Seasonality Units Sold (Pie Chart)
    seasonal_units = df.groupby("Seasonality")["Units Sold"].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(seasonal_units, labels=seasonal_units.index, autopct='%1.1f%%', startangle=130, colors=sns.color_palette('Set2'))
    plt.title("Total Units Sold by Seasonality")
    plt.tight_layout()
    plt.savefig(output_dir / '02_seasonal_units_distribution.jpeg')
    plt.close()

    # Chart 3: Top 10 Highest Demand Products
    plt.figure(figsize=(12, 6))
    top_10 = product_summary.sort_values(by='Total_Demand', ascending=False).head(10)
    sns.barplot(
        data=top_10,
        x='Total_Demand',
        y='Product ID',
        hue='Product ID',
        palette='viridis',
        legend=False,
    )
    plt.title('Top 10 Highest Demand Products')
    plt.xlabel('Total Units Sold')
    plt.ylabel('Product ID')
    plt.tight_layout()
    plt.savefig(output_dir / '03_top_demand_products.jpeg')
    plt.close()

    # Chart 4: Daily Demand Trend & 7-Day Moving Average
    daily_demand = df.groupby('Date')['Units Sold'].sum().reset_index()
    daily_demand['7_Day_Moving_Avg'] = daily_demand['Units Sold'].rolling(window=7).mean()
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily_demand['Date'], daily_demand['Units Sold'], alpha=0.3, label='Daily Units Sold', color='gray')
    plt.plot(daily_demand['Date'], daily_demand['7_Day_Moving_Avg'], label='7-Day Moving Average Trend', color='red', linewidth=2)
    plt.title('Daily Total Demand with 7-Day Moving Average (2025–2026)')
    plt.xlabel('Date')
    plt.ylabel('Units Sold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / '04_demand_trend_7day_moving_avg.jpeg')
    plt.close()

    # Chart 5: Actual Demand vs Demand Forecast Accuracy
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_forecast.sample(min(1000, len(df_forecast))), x='Demand Forecast', y='Units Sold', alpha=0.5, color='teal')
    plt.plot([0, df_forecast['Demand Forecast'].max()], [0, df_forecast['Demand Forecast'].max()], 'r--', label='Ideal Forecast (100% Match)')
    plt.title('Baseline Demand Forecast vs Actual Units Sold')
    plt.xlabel('Baseline Forecasted Demand')
    plt.ylabel('Actual Units Sold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / '05_forecast_vs_actual.jpeg')
    plt.close()

    # Chart 6: High Demand Product Categories (Units Sold Count Ranking)
    category_demand = df.groupby('Category')['Units Sold'].sum().reset_index()
    category_demand = category_demand.sort_values(by='Units Sold', ascending=False)
    
    plt.figure(figsize=(10, 6))
    ax=sns.barplot(
        data=category_demand,
        x='Category',
        y='Units Sold',
        hue='Category',
        palette='magma',
        legend=False
    )
    for container in ax.containers: ax.bar_label(container, fmt='%.2f', padding=2)
    plt.title('High Demand Product Categories (Total Units Sold)')
    plt.xlabel('Product Category')
    plt.ylabel('Total Units Sold Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / '06_high_demand_categories.jpeg')
    plt.close()

    print(f"\nAll 6 analysis charts successfully saved to: {output_dir}")


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent.parent
    
    # Path Resolution
    cleaned_data_path = project_dir / "outputs" / "retail_store_inventory_cleaned.csv"
    
    if not cleaned_data_path.exists():
        cleaned_data_path = project_dir / "data" / "cleaned_retail_inventory_2025_2026.csv"

    if not cleaned_data_path.exists():
        cleaned_data_path = project_dir / "retail_store_inventory_extended_messy_2025_2026.xlsx"

    df = pd.read_excel(cleaned_data_path) if cleaned_data_path.suffix == '.xlsx' else pd.read_csv(cleaned_data_path)
    run_data_analysis(df)