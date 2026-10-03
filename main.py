"""
Master CLI Entry Point for Market Basket Analysis System.
Orchestrates end-to-end data cleaning, EDA, frequent pattern mining, association rule extraction,
business insights, network graph generation, and Streamlit dashboard launching.
"""

import os
import sys
import argparse
import logging
import subprocess
import pandas as pd

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import run_pipeline_ingestion
from src.encoder import load_cleaned_data, create_basket_lists, encode_transactions_sparse
from src.eda import perform_eda
from src.frequent_mining import compare_algorithms, filter_frequent_items_matrix, mine_fpgrowth
from src.rule_generator import run_rule_pipeline
from src.insights import generate_business_insights, run_country_segment_analysis, get_retail_action_plan
from src.network_graph import build_product_network, plot_network_graph
from src.scalability import StageProfiler, load_dataset_with_sampling, BatchTransactionProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Scalable Market Basket Analysis System")
    parser.add_argument("--clean", action="store_true", help="Run raw data ingestion and cleaning")
    parser.add_argument("--eda", action="store_true", help="Run Exploratory Data Analysis")
    parser.add_argument("--benchmark", action="store_true", help="Run Apriori vs FP-Growth benchmark comparison")
    parser.add_argument("--sample", type=float, default=None, help="Sample ratio for fast execution (e.g. 0.1 for 10% sample)")
    parser.add_argument("--full", action="store_true", help="Run pipeline on full dataset")
    parser.add_argument("--country", type=str, default="All", help="Country filter (e.g. 'United Kingdom', 'Germany', 'France', 'EIRE', 'All')")
    parser.add_argument("--support", type=float, default=0.02, help="Minimum support threshold (default: 0.02)")
    parser.add_argument("--confidence", type=float, default=0.30, help="Minimum confidence threshold (default: 0.30)")
    parser.add_argument("--lift", type=float, default=1.20, help="Minimum lift threshold (default: 1.20)")
    parser.add_argument("--app", action="store_true", help="Launch Streamlit interactive web dashboard")
    return parser.parse_args()


def run_full_pipeline(args):
    """Run end-to-end Market Basket Analysis pipeline."""
    logging.info("Starting End-to-End Market Basket Analysis Pipeline...")

    # Stage 1: Data Ingestion & Hygiene
    with StageProfiler("Stage 1 & 2: Data Ingestion & Cleaning"):
        if not os.path.exists("data/processed/cleaned_transactions.parquet") or args.clean:
            df_clean = run_pipeline_ingestion()
        else:
            df_clean = load_dataset_with_sampling(sample_ratio=args.sample)

    if args.country and args.country.upper() != "ALL":
        logging.info(f"Filtering dataset by Country = '{args.country}'...")
        df_clean = df_clean[df_clean["Country"].str.upper() == args.country.upper()]
        logging.info(f"Filtered dataset: {df_clean['InvoiceNo'].nunique():,} invoices.")

    # Stage 2: EDA
    if args.eda:
        with StageProfiler("Stage 3: Exploratory Data Analysis"):
            perform_eda(df_clean)

    # Stage 3: Basket Encoding
    with StageProfiler("Stage 3: Basket Grouping & Sparse Encoding"):
        baskets, invoice_ids = create_basket_lists(df_clean)
        _, sparse_matrix, item_names = encode_transactions_sparse(baskets)

    # Stage 4: Algorithm Benchmark / Pattern Mining
    if args.benchmark:
        with StageProfiler("Stage 4: Apriori vs FP-Growth Benchmark"):
            compare_algorithms(sparse_matrix, item_names, min_supports=[0.015, 0.02, 0.03, 0.05])

    # Stage 5: Rule Generation
    with StageProfiler("Stage 5: Association Rule Extraction"):
        df_bool = filter_frequent_items_matrix(sparse_matrix, item_names, min_item_support=args.support * 0.8)
        frequent_itemsets, _, _ = mine_fpgrowth(df_bool, min_support=args.support, max_len=4)
        rules, top_lift, top_conf, misleading = run_rule_pipeline(
            min_support=args.support, min_confidence=args.confidence, min_lift=args.lift
        )

    # Stage 6: Business Insights & Network Graph
    with StageProfiler("Stage 6: Business Insights & Network Graph"):
        if not top_lift.empty:
            insights = generate_business_insights(top_lift.head(10))
            actions = get_retail_action_plan(top_lift)
            G = build_product_network(rules, min_lift=max(args.lift, 2.0))
            plot_network_graph(G)

        run_country_segment_analysis(df_clean)

    # Stage 7: Scalability Demo
    with StageProfiler("Stage 7: Out-of-Core Batch Processor"):
        batch_proc = BatchTransactionProcessor(chunk_size=50000)
        if os.path.exists("data/processed/cleaned_transactions.csv"):
            batch_proc.process_csv_chunks("data/processed/cleaned_transactions.csv")

    logging.info("Full Market Basket Analysis Pipeline Completed Successfully!")
    print("\n=======================================================")
    print(f"SUMMARY: Mined {len(rules):,} Rules across {len(baskets):,} Invoices.")
    print("=======================================================\n")


def main():
    args = parse_args()
    if args.app:
        logging.info("Launching Streamlit Interactive Dashboard...")
        venv_python = sys.executable
        subprocess.run([venv_python, "-m", "streamlit", "run", "app/streamlit_app.py"])
    else:
        run_full_pipeline(args)


if __name__ == "__main__":
    main()
