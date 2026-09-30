"""
Frequent Pattern Mining Module for Market Basket Analysis.
Implements and benchmarks Apriori vs FP-Growth algorithms across multiple support thresholds.
Measures execution runtime, memory usage, and itemset yields.
"""

import os
import sys
import time
import json
import logging
import tracemalloc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, fpgrowth

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.encoder import load_cleaned_data, create_basket_lists, encode_transactions_sparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def filter_frequent_items_matrix(sparse_matrix, item_names, min_item_support=0.01):
    """
    Rapidly filter SciPy sparse matrix to columns meeting min_item_support.
    Returns dense boolean DataFrame of relevant products.
    """
    n_baskets = sparse_matrix.shape[0]
    item_counts = np.array(sparse_matrix.sum(axis=0)).flatten()
    item_supports = item_counts / n_baskets
    
    mask = item_supports >= min_item_support
    frequent_indices = np.where(mask)[0]
    frequent_items = [item_names[i] for i in frequent_indices]
    
    logging.info(f"Filtered matrix columns from {len(item_names):,} to {len(frequent_items):,} "
                 f"products meeting support >= {min_item_support:.4f}.")
    
    dense_matrix = sparse_matrix[:, frequent_indices].toarray().astype(bool)
    return pd.DataFrame(dense_matrix, columns=frequent_items)


def mine_apriori(df_bool, min_support=0.02, use_colnames=True, max_len=4):
    """Run Apriori algorithm with runtime and memory tracking."""
    tracemalloc.start()
    t0 = time.perf_counter()
    
    itemsets = apriori(df_bool, min_support=min_support, use_colnames=use_colnames, max_len=max_len, low_memory=True)
    
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    peak_mb = peak / (1024 * 1024)
    itemsets["length"] = itemsets["itemsets"].apply(len)
    return itemsets, round(elapsed, 4), round(peak_mb, 2)


def mine_fpgrowth(df_bool, min_support=0.02, use_colnames=True, max_len=4):
    """Run FP-Growth algorithm with runtime and memory tracking."""
    tracemalloc.start()
    t0 = time.perf_counter()
    
    itemsets = fpgrowth(df_bool, min_support=min_support, use_colnames=use_colnames, max_len=max_len)
    
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    peak_mb = peak / (1024 * 1024)
    itemsets["length"] = itemsets["itemsets"].apply(len)
    return itemsets, round(elapsed, 4), round(peak_mb, 2)


def compare_algorithms(sparse_matrix, item_names, min_supports=[0.015, 0.02, 0.03, 0.05], max_len=4, output_dir="reports/frequent_mining"):
    """
    Benchmark Apriori vs FP-Growth across multiple min_support thresholds.
    """
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Comparing Apriori vs FP-Growth across min_supports: {min_supports} (max_len={max_len})...")
    
    min_needed = min(min_supports) * 0.9
    df_bool = filter_frequent_items_matrix(sparse_matrix, item_names, min_item_support=min_needed)

    benchmark_results = []
    frequent_itemsets_dict = {}

    for supp in min_supports:
        logging.info(f"Mining frequent itemsets at min_support = {supp}...")
        
        # Run FP-Growth
        fp_itemsets, fp_time, fp_mem = mine_fpgrowth(df_bool, min_support=supp, max_len=max_len)
        frequent_itemsets_dict[supp] = fp_itemsets

        # Run Apriori
        ap_itemsets, ap_time, ap_mem = mine_apriori(df_bool, min_support=supp, max_len=max_len)

        itemset_count = len(fp_itemsets)
        speedup = round(ap_time / max(fp_time, 0.0001), 2)
        
        benchmark_results.append({
            "min_support": supp,
            "frequent_itemsets_count": itemset_count,
            "apriori_runtime_sec": ap_time,
            "fpgrowth_runtime_sec": fp_time,
            "speedup_factor": speedup,
            "apriori_peak_mem_mb": ap_mem,
            "fpgrowth_peak_mem_mb": fp_mem
        })
        
        logging.info(f"Support {supp}: {itemset_count:,} itemsets | "
                     f"Apriori: {ap_time}s ({ap_mem}MB) vs FP-Growth: {fp_time}s ({fp_mem}MB) -> "
                     f"FP-Growth is {speedup}x faster")

    results_df = pd.DataFrame(benchmark_results)
    results_df.to_csv(os.path.join(output_dir, "algorithm_comparison.csv"), index=False)

    # Plot Runtime Comparison
    plt.figure(figsize=(10, 5))
    plt.plot(results_df["min_support"], results_df["apriori_runtime_sec"], marker="o", linewidth=2.5, color="#e74c3c", label="Apriori")
    plt.plot(results_df["min_support"], results_df["fpgrowth_runtime_sec"], marker="s", linewidth=2.5, color="#2ecc71", label="FP-Growth")
    plt.title("Execution Runtime Comparison: Apriori vs FP-Growth")
    plt.xlabel("Minimum Support Threshold (min_support)")
    plt.ylabel("Execution Time (Seconds)")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    plt.savefig(os.path.join(output_dir, "runtime_comparison.png"), dpi=300)
    plt.close()

    # Plot Support vs Itemset Count Tradeoff
    plt.figure(figsize=(10, 5))
    bars = plt.bar(results_df["min_support"].astype(str), results_df["frequent_itemsets_count"], color="#8e44ad")
    plt.title("Support vs Frequent Itemset Count Tradeoff")
    plt.xlabel("Minimum Support Threshold (min_support)")
    plt.ylabel("Number of Frequent Itemsets Mined")
    for idx, val in enumerate(results_df["frequent_itemsets_count"]):
        plt.text(idx, val + max(results_df["frequent_itemsets_count"])*0.02, f"{val:,}", ha="center", fontweight="bold")
    plt.savefig(os.path.join(output_dir, "support_vs_itemsets.png"), dpi=300)
    plt.close()

    return results_df, frequent_itemsets_dict


if __name__ == "__main__":
    df = load_cleaned_data()
    baskets, _ = create_basket_lists(df)
    _, sparse_matrix, item_names = encode_transactions_sparse(baskets)
    
    benchmark_df, itemsets_dict = compare_algorithms(sparse_matrix, item_names, min_supports=[0.015, 0.02, 0.03, 0.05], max_len=4)
    print("\n--- Algorithm Benchmark Results ---")
    print(benchmark_df.to_string(index=False))
