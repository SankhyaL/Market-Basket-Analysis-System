"""
Data Loader & Cleaner Module for Market Basket Analysis.
Ingests raw transaction dataset, handles missing/invalid values, filters non-product items,
standardizes descriptions, and exports clean transaction table.
"""

import os
import re
import yaml
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_config(config_path="config.yaml"):
    """Load system configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def load_raw_data(excel_path="online_retail_II.xlsx"):
    """
    Load raw transaction data from Excel file (both sheets).
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Raw data file not found at: {excel_path}")
    
    logging.info(f"Loading raw data from Excel file: {excel_path}...")
    excel_file = pd.ExcelFile(excel_path)
    dfs = []
    for sheet in excel_file.sheet_names:
        logging.info(f"Reading sheet: {sheet}...")
        df_sheet = pd.read_excel(excel_file, sheet_name=sheet)
        dfs.append(df_sheet)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    logging.info(f"Raw data loaded successfully. Total raw records: {len(combined_df):,}")
    
    # Standardize column names
    column_mapping = {
        "Invoice": "InvoiceNo",
        "Customer ID": "CustomerID",
        "Price": "Price"
    }
    combined_df = combined_df.rename(columns=column_mapping)
    return combined_df


def clean_data(df, config=None):
    """
    Clean raw transaction DataFrame:
    - Drop missing InvoiceNo or Description
    - Remove cancelled orders (InvoiceNo starts with 'C')
    - Remove non-positive quantities and prices
    - Clean and standardize Descriptions and StockCodes
    - Remove non-product stock codes and service fees
    """
    if config is None:
        config = load_config()

    initial_count = len(df)
    logging.info(f"Starting data cleaning process on {initial_count:,} records...")

    # 1. Convert types and drop missing critical values
    cleaned = df.copy()
    cleaned["InvoiceNo"] = cleaned["InvoiceNo"].astype(str).str.strip()
    
    # Drop records with missing InvoiceNo or Description
    cleaned = cleaned.dropna(subset=["InvoiceNo", "Description"])
    logging.info(f"Records after dropping missing InvoiceNo/Description: {len(cleaned):,}")

    # 2. Remove cancelled orders (Invoice starting with 'C' or 'c')
    cleaned = cleaned[~cleaned["InvoiceNo"].str.upper().str.startswith("C")]
    logging.info(f"Records after removing cancelled orders ('C'): {len(cleaned):,}")

    # 3. Filter positive Quantity and Price
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    cleaned = cleaned[(cleaned["Quantity"] > 0) & (cleaned["Price"] > 0)]
    logging.info(f"Records after keeping positive Quantity & Price: {len(cleaned):,}")

    # 4. Standardize StockCode and Description
    cleaned["StockCode"] = cleaned["StockCode"].astype(str).str.strip().str.upper()
    cleaned["Description"] = cleaned["Description"].astype(str).str.strip().str.upper()
    
    # Normalize spaces in Description
    cleaned["Description"] = cleaned["Description"].apply(lambda x: re.sub(r"\s+", " ", x))

    # 5. Filter out non-product StockCodes and Service/Adjustment fees
    non_product_codes = config.get("cleaning", {}).get("non_product_codes", [
        "POST", "PADS", "M", "DOT", "C2", "BANK CHARGES", "TEST001", "TEST002",
        "ADJUST", "ADJUST2", "AMAZONFEE", "CRUK", "D"
    ])
    non_product_codes = set([code.upper() for code in non_product_codes])
    
    # StockCode filtering
    cleaned = cleaned[~cleaned["StockCode"].isin(non_product_codes)]
    
    # Keywords in Description indicating non-product entries
    service_keywords = [
        "POSTAGE", "MANUAL", "BANK CHARGES", "CARRIAGE", "DISCOUNT", "AMAZON FEE",
        "SAMPLES", "CHECK", "DAMAGED", "LOST", "DESTROYED", "WRONG", "BARCODE",
        "ADJUSTMENT", "FEES", "CRUK"
    ]
    pattern = "|".join(service_keywords)
    cleaned = cleaned[~cleaned["Description"].str.contains(pattern, case=False, regex=True)]

    logging.info(f"Records after filtering non-product stock codes & service items: {len(cleaned):,}")

    # Format CustomerID cleanly (convert float to int string or NaN to 'GUEST')
    cleaned["CustomerID"] = cleaned["CustomerID"].apply(
        lambda x: str(int(x)) if pd.notnull(x) and str(x).replace(".", "").isdigit() else "GUEST"
    )

    # Convert InvoiceDate to datetime
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")

    # Final summary statistics
    logging.info(f"Data cleaning completed. Cleaned dataset contains {len(cleaned):,} records "
                 f"({(len(cleaned)/initial_count)*100:.2f}% of raw dataset).")
    
    # Ensure correct column ordering
    output_cols = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "CustomerID", "Country"]
    return cleaned[output_cols]


def run_pipeline_ingestion(excel_path="online_retail_II.xlsx",
                           parquet_out="data/processed/cleaned_transactions.parquet",
                           csv_out="data/processed/cleaned_transactions.csv"):
    """
    Run full Segment 2 Ingestion & Cleaning pipeline and save outputs.
    """
    os.makedirs("data/processed", exist_ok=True)
    raw_df = load_raw_data(excel_path)
    clean_df = clean_data(raw_df)
    
    logging.info(f"Saving cleaned transactions to Parquet: {parquet_out}...")
    clean_df.to_parquet(parquet_out, index=False)
    
    logging.info(f"Saving cleaned transactions to CSV: {csv_out}...")
    clean_df.to_csv(csv_out, index=False)
    
    return clean_df


if __name__ == "__main__":
    df = run_pipeline_ingestion()
    print("\n--- Cleaned Data Sample ---")
    print(df.head(10))
    print("\n--- Summary Statistics ---")
    print(f"Total Unique Invoices: {df['InvoiceNo'].nunique():,}")
    print(f"Total Unique Items: {df['Description'].nunique():,}")
    print(f"Total Unique Customers: {df['CustomerID'].nunique():,}")
    print(f"Total Countries: {df['Country'].nunique():,}")
