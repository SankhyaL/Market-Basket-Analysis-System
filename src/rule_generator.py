"""
Association Rule Generation Module for Market Basket Analysis.
Generates association rules, computes evaluation metrics (support, confidence, lift, leverage, conviction),
filters rules, ranks top rules, and identifies misleading high-confidence/low-lift rules.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import association_rules

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.encoder import load_cleaned_data, create_basket_lists, encode_transactions_sparse
from src.frequent_mining import filter_frequent_items_matrix, mine_fpgrowth

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def format_itemset_str(itemset):
    """Convert frozenset/set of items to readable comma-separated string."""
    return ", ".join(sorted(list(itemset)))


def generate_rules(frequent_itemsets, min_confidence=0.3, min_lift=1.2, metric="confidence"):
    """
    Generate association rules from frequent itemsets and calculate all metrics.
    """
    logging.info(f"Generating association rules (metric={metric}, min_threshold={min_confidence})...")
    if frequent_itemsets.empty:
        logging.warning("Frequent itemsets DataFrame is empty. Returning empty rules DataFrame.")
        return pd.DataFrame()

    rules = association_rules(frequent_itemsets, metric=metric, min_threshold=min_confidence)
    
    if rules.empty:
        logging.warning("No rules met the initial confidence threshold.")
        return pd.DataFrame()

    # Filter by min_lift
    rules = rules[rules["lift"] >= min_lift].copy()
    
    # Add human-readable string columns for antecedents and consequents
    rules["antecedents_str"] = rules["antecedents"].apply(format_itemset_str)
    rules["consequents_str"] = rules["consequents"].apply(format_itemset_str)
    rules["rule_str"] = rules["antecedents_str"] + "  ==>  " + rules["consequents_str"]

    # Round numerical metrics
    metrics_cols = ["antecedent support", "consequent support", "support", "confidence", "lift", "leverage", "conviction"]
    for col in metrics_cols:
        if col in rules.columns:
            rules[col] = rules[col].round(4)
            
    logging.info(f"Generated {len(rules):,} association rules meeting confidence >= {min_confidence} and lift >= {min_lift}.")
    return rules


def identify_misleading_rules(frequent_itemsets, min_confidence=0.4, lift_tolerance=0.15):
    """
    Identify misleading rules: High confidence (>= min_confidence) but Lift ≈ 1.0 (between 1-tol and 1+tol).
    These indicate that the consequent is purchased independently of the antecedent (spurious correlation).
    """
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return pd.DataFrame()

    misleading = rules[(rules["lift"] >= (1.0 - lift_tolerance)) & (rules["lift"] <= (1.0 + lift_tolerance))].copy()
    misleading["antecedents_str"] = misleading["antecedents"].apply(format_itemset_str)
    misleading["consequents_str"] = misleading["consequents"].apply(format_itemset_str)
    misleading["rule_str"] = misleading["antecedents_str"] + "  ==>  " + misleading["consequents_str"]
    misleading["explanation"] = misleading.apply(
        lambda r: f"High confidence ({r['confidence']:.2%}) is misleading because '{r['consequents_str']}' has high base support ({r['consequent support']:.2%}) and Lift ({r['lift']:.2f}) ≈ 1.0.",
        axis=1
    )
    return misleading.sort_values(by="confidence", ascending=False)


def run_rule_pipeline(min_support=0.02, min_confidence=0.3, min_lift=1.2, output_dir="reports/association_rules"):
    """
    Run full Segment 5 Rule Generation Pipeline and save top rule tables.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load data & mine frequent itemsets
    df = load_cleaned_data()
    baskets, _ = create_basket_lists(df)
    _, sparse_matrix, item_names = encode_transactions_sparse(baskets)
    
    df_bool = filter_frequent_items_matrix(sparse_matrix, item_names, min_item_support=min_support*0.8)
    frequent_itemsets, _, _ = mine_fpgrowth(df_bool, min_support=min_support, max_len=4)
    
    # 2. Generate and filter rules
    rules = generate_rules(frequent_itemsets, min_confidence=min_confidence, min_lift=min_lift)
    
    if rules.empty:
        logging.warning("No rules generated with given parameters.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # 3. Top 20 rules by Lift
    top_by_lift = rules.sort_values(by="lift", ascending=False).head(20)
    top_by_lift.to_csv(os.path.join(output_dir, "top_20_rules_by_lift.csv"), index=False)

    # 4. Top 20 rules by Confidence
    top_by_conf = rules.sort_values(by="confidence", ascending=False).head(20)
    top_by_conf.to_csv(os.path.join(output_dir, "top_20_rules_by_confidence.csv"), index=False)

    # 5. Misleading rules detection
    misleading_rules = identify_misleading_rules(frequent_itemsets, min_confidence=0.3)
    misleading_rules.to_csv(os.path.join(output_dir, "misleading_rules.csv"), index=False)

    logging.info(f"Top rules saved to {output_dir}. Top rule by Lift: '{top_by_lift.iloc[0]['rule_str']}' (Lift={top_by_lift.iloc[0]['lift']})")
    
    return rules, top_by_lift, top_by_conf, misleading_rules


if __name__ == "__main__":
    rules, top_lift, top_conf, misleading = run_rule_pipeline(min_support=0.02, min_confidence=0.3, min_lift=1.2)
    
    print("\n--- TOP 10 ASSOCIATION RULES BY LIFT ---")
    cols_show = ["rule_str", "support", "confidence", "lift", "conviction"]
    print(top_lift[cols_show].head(10).to_string(index=False))
    
    if not misleading.empty:
        print("\n--- MISLEADING RULES DETECTED (High Confidence, Lift ≈ 1.0) ---")
        print(misleading[["rule_str", "confidence", "consequent support", "lift", "explanation"]].head(5).to_string(index=False))
