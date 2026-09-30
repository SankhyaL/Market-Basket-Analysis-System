"""
Exploratory Data Analysis (EDA) Module for Market Basket Analysis.
Generates transaction statistics, item distributions, basket size statistics,
country/time trends, and saves visualizations.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.encoder import load_cleaned_data, create_basket_lists

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set aesthetic styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11, 'figure.autolayout': True})


def perform_eda(df=None, output_dir="reports/eda"):
    """
    Perform comprehensive EDA on cleaned transaction dataset.
    """
    if df is None:
        df = load_cleaned_data()

    os.makedirs(output_dir, exist_ok=True)
    logging.info("Starting Exploratory Data Analysis...")

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Revenue"] = df["Quantity"] * df["Price"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # 1. Basket Size Analysis
    basket_sizes = df.groupby("InvoiceNo")["Description"].nunique()
    basket_stats = {
        "total_invoices": int(len(basket_sizes)),
        "mean_basket_size": round(float(basket_sizes.mean()), 2),
        "median_basket_size": float(basket_sizes.median()),
        "min_basket_size": int(basket_sizes.min()),
        "max_basket_size": int(basket_sizes.max()),
        "p95_basket_size": int(np.percentile(basket_sizes, 95))
    }
    
    # Plot Basket Size Distribution
    plt.figure(figsize=(10, 5))
    sns.histplot(basket_sizes, bins=range(1, 50), color="#3498db", kde=True)
    plt.axvline(basket_sizes.mean(), color="#e74c3c", linestyle="--", label=f"Mean ({basket_stats['mean_basket_size']})")
    plt.axvline(basket_sizes.median(), color="#2ecc71", linestyle="-", label=f"Median ({basket_stats['median_basket_size']})")
    plt.title("Basket Size Distribution (Items per Invoice)")
    plt.xlabel("Number of Unique Items in Basket")
    plt.ylabel("Invoice Count")
    plt.xlim(1, 50)
    plt.legend()
    plt.savefig(os.path.join(output_dir, "basket_size_dist.png"), dpi=300)
    plt.close()

    # 2. Top Best-Selling Products (by Frequency & Revenue)
    top_freq = df["Description"].value_counts().head(20)
    top_revenue = df.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(20)
    
    # Plot Top 20 Best-Selling Items by Frequency
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_freq.values, y=top_freq.index, palette="viridis")
    plt.title("Top 20 Most Frequently Purchased Products")
    plt.xlabel("Number of Transactions")
    plt.ylabel("Product Description")
    plt.savefig(os.path.join(output_dir, "top_20_products_freq.png"), dpi=300)
    plt.close()

    # Plot Top 20 Best-Selling Items by Revenue
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_revenue.values, y=top_revenue.index, palette="magma")
    plt.title("Top 20 Products by Total Generated Revenue (£)")
    plt.xlabel("Total Revenue (£)")
    plt.ylabel("Product Description")
    plt.savefig(os.path.join(output_dir, "top_20_products_revenue.png"), dpi=300)
    plt.close()

    # 3. Country Analysis
    country_sales = df.groupby("Country").agg(
        Invoices=("InvoiceNo", "nunique"),
        Total_Revenue=("Revenue", "sum")
    ).sort_values(by="Invoices", ascending=False)
    
    plt.figure(figsize=(12, 6))
    top_countries = country_sales.head(15)
    sns.barplot(x=top_countries["Invoices"], y=top_countries.index, palette="crest")
    plt.title("Top 15 Countries by Transaction Volume (Invoices)")
    plt.xlabel("Number of Unique Invoices")
    plt.ylabel("Country")
    plt.savefig(os.path.join(output_dir, "top_countries.png"), dpi=300)
    plt.close()

    # 4. Monthly Sales Trend
    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    monthly_trend = df.groupby("YearMonth").agg(
        Invoices=("InvoiceNo", "nunique"),
        Revenue=("Revenue", "sum")
    )
    
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()
    
    monthly_trend["Invoices"].plot(kind="line", ax=ax1, color="#2980b9", marker="o", label="Invoices")
    monthly_trend["Revenue"].plot(kind="line", ax=ax2, color="#e67e22", marker="s", linestyle="--", label="Revenue (£)")
    
    ax1.set_title("Monthly Transaction Volume and Total Revenue Trend (2009 - 2011)")
    ax1.set_ylabel("Transaction Count (Invoices)", color="#2980b9")
    ax2.set_ylabel("Total Revenue (£)", color="#e67e22")
    ax1.grid(True, linestyle=":", alpha=0.6)
    plt.savefig(os.path.join(output_dir, "monthly_trend.png"), dpi=300)
    plt.close()

    # Save summary json stats
    stats_out = {
        "basket_stats": basket_stats,
        "top_5_items_freq": top_freq.head(5).to_dict(),
        "top_5_items_revenue": {k: round(float(v), 2) for k, v in top_revenue.head(5).items()},
        "top_5_countries_invoices": country_sales["Invoices"].head(5).to_dict()
    }
    with open(os.path.join(output_dir, "eda_summary.json"), "w") as f:
        json.dump(stats_out, f, indent=2)

    logging.info(f"EDA complete! Plots and statistics saved to: {output_dir}")
    return stats_out, basket_sizes, top_freq, country_sales


if __name__ == "__main__":
    stats, b_sizes, top_freq, c_sales = perform_eda()
    print("\n--- EDA Summary Metrics ---")
    print(json.dumps(stats, indent=2))
