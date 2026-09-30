"""
Scalability & Batch Processing Engine for Market Basket Analysis.
Implements chunked out-of-core transaction processing, dataset sampling CLI support,
stage-level memory & execution profiling, and batch count merging.
"""

import os
import sys
import time
import json
import logging
import tracemalloc
from collections import defaultdict, Counter
import pandas as pd
import numpy as np

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class StageProfiler:
    """Context manager for logging execution runtime and memory usage per stage."""
    def __init__(self, stage_name):
        self.stage_name = stage_name

    def __enter__(self):
        tracemalloc.start()
        self.t0 = time.perf_counter()
        logging.info(f"=== [START STAGE] {self.stage_name} ===")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mb = peak / (1024 * 1024)
        logging.info(f"=== [COMPLETED STAGE] {self.stage_name} | Elapsed: {elapsed:.2f}s | Peak Memory: {peak_mb:.2f} MB ===")


class BatchTransactionProcessor:
    """
    Out-of-core batch processor for massive transaction datasets.
    Processes data in chunks, computes item frequencies and pair co-occurrences,
    and merges partial counts across chunks.
    """
    def __init__(self, chunk_size=50000):
        self.chunk_size = chunk_size
        self.item_counts = Counter()
        self.pair_counts = Counter()
        self.total_baskets = 0

    def process_csv_chunks(self, csv_filepath):
        """Process CSV file in chunked iterations."""
        logging.info(f"Processing transactions in chunks of {self.chunk_size:,} from: {csv_filepath}")
        chunk_iter = pd.read_csv(csv_filepath, chunksize=self.chunk_size)
        
        for idx, chunk in enumerate(chunk_iter):
            logging.info(f"Processing chunk {idx+1} ({len(chunk):,} rows)...")
            
            # Simple clean inside chunk
            chunk = chunk[(chunk["Quantity"] > 0) & (chunk["Price"] > 0)].dropna(subset=["InvoiceNo", "Description"])
            
            # Group chunk baskets
            grouped = chunk.groupby("InvoiceNo")["Description"].unique()
            self.total_baskets += len(grouped)
            
            for items in grouped:
                items = sorted(list(set(items)))
                # Update item counts
                for item in items:
                    self.item_counts[item] += 1
                # Update pair counts
                for i in range(len(items)):
                    for j in range(i + 1, len(items)):
                        self.pair_counts[(items[i], items[j])] += 1
                        
        logging.info(f"Out-of-core batch processing complete. Total Baskets: {self.total_baskets:,}, "
                     f"Unique Items: {len(self.item_counts):,}, Unique Pairs: {len(self.pair_counts):,}")

    def get_frequent_pairs(self, min_support=0.02):
        """Extract frequent 2-itemsets directly from accumulated pair counts."""
        min_count = self.total_baskets * min_support
        frequent_pairs = []
        
        for (item_a, item_b), count in self.pair_counts.items():
            if count >= min_count:
                supp = count / self.total_baskets
                supp_a = self.item_counts[item_a] / self.total_baskets
                supp_b = self.item_counts[item_b] / self.total_baskets
                conf_a_b = supp / supp_a
                lift = supp / (supp_a * supp_b)
                
                frequent_pairs.append({
                    "antecedent": item_a,
                    "consequent": item_b,
                    "support": round(supp, 4),
                    "confidence": round(conf_a_b, 4),
                    "lift": round(lift, 2)
                })
                
        df_rules = pd.DataFrame(frequent_pairs)
        if not df_rules.empty:
            df_rules = df_rules.sort_values(by="lift", ascending=False)
        return df_rules


def load_dataset_with_sampling(filepath="data/processed/cleaned_transactions.csv", sample_ratio=None, random_state=42):
    """
    Load dataset with optional sampling (for fast iteration or full dataset execution).
    """
    if not os.path.exists(filepath):
        parquet_path = filepath.replace(".csv", ".parquet")
        if os.path.exists(parquet_path):
            df = pd.read_parquet(parquet_path)
        else:
            raise FileNotFoundError(f"Cleaned dataset not found at {filepath}")
    else:
        df = pd.read_csv(filepath)

    if sample_ratio and 0.0 < sample_ratio < 1.0:
        # Sample by unique InvoiceNo to preserve complete baskets
        unique_invoices = df["InvoiceNo"].unique()
        sample_size = int(len(unique_invoices) * sample_ratio)
        np.random.seed(random_state)
        sampled_invoices = set(np.random.choice(unique_invoices, size=sample_size, replace=False))
        df = df[df["InvoiceNo"].isin(sampled_invoices)].copy()
        logging.info(f"Sampled dataset: {sample_ratio*100:.1f}% ({len(sampled_invoices):,} invoices, {len(df):,} rows).")
    else:
        logging.info(f"Loaded full dataset: {df['InvoiceNo'].nunique():,} invoices, {len(df):,} rows.")

    return df


if __name__ == "__main__":
    with StageProfiler("Out-of-Core Chunked Processing Demo"):
        processor = BatchTransactionProcessor(chunk_size=50000)
        processor.process_csv_chunks("data/processed/cleaned_transactions.csv")
        rules_out = processor.get_frequent_pairs(min_support=0.02)
        print("\n--- Out-of-Core Batch Rules Mined (Top 5) ---")
        print(rules_out.head(5).to_string(index=False))
