"""
Business Insight & Strategy Layer for Market Basket Analysis.
Translates statistical association rules into natural language business recommendations,
performs country/region segment analysis, and generates concrete retail action plans.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.encoder import load_cleaned_data, create_basket_lists, encode_transactions_sparse
from src.frequent_mining import filter_frequent_items_matrix, mine_fpgrowth
from src.rule_generator import generate_rules

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def translate_rule_to_insight(row):
    """Translate single association rule row into actionable business text."""
    ant = row["antecedents_str"]
    cons = row["consequents_str"]
    conf_pct = row["confidence"] * 100
    lift_val = row["lift"]
    
    insight_text = (
        f"Customers who purchase '{ant}' are {lift_val:.1f}x more likely to also purchase '{cons}' "
        f"(Confidence: {conf_pct:.1f}%, Support: {row['support']*100:.2f}%)."
    )
    
    if lift_val >= 15.0:
        recommendation = f"HIGH PRIORITY BUNDLE: Create a combo pack '{ant} + {cons}' or place them side-by-side on store shelves."
    elif lift_val >= 5.0:
        recommendation = f"CROSS-SELL PROMPT: Show '{cons}' as a recommended 'Frequently Bought Together' item on the checkout screen when '{ant}' is added to cart."
    else:
        recommendation = f"PROMOTIONAL LINKAGE: Offer a 10% discount on '{cons}' when purchasing '{ant}'."
        
    return {
        "rule": row["rule_str"],
        "antecedents": ant,
        "consequents": cons,
        "confidence_pct": round(conf_pct, 1),
        "lift": round(lift_val, 2),
        "insight": insight_text,
        "actionable_recommendation": recommendation
    }


def generate_business_insights(top_rules_df):
    """Translate DataFrame of top rules into structured insights."""
    if top_rules_df.empty:
        return []
    
    insights = []
    for _, row in top_rules_df.iterrows():
        insights.append(translate_rule_to_insight(row))
    return insights


def run_country_segment_analysis(df=None, top_countries=["United Kingdom", "Germany", "France", "EIRE"],
                                 output_dir="reports/insights"):
    """
    Run Market Basket Analysis separately by Country to identify regional basket behavior.
    """
    if df is None:
        df = load_cleaned_data()

    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Running country segment analysis for: {top_countries}...")
    
    country_results = {}

    for country in top_countries:
        country_df = df[df["Country"] == country]
        if country_df.empty:
            continue
            
        baskets, _ = create_basket_lists(country_df)
        if len(baskets) < 50:
            logging.info(f"Skipping {country} - insufficient transactions ({len(baskets)}).")
            continue
            
        _, sparse_matrix, item_names = encode_transactions_sparse(baskets)
        
        # Adaptive min_support based on country transaction volume
        supp_thresh = 0.02 if country == "United Kingdom" else 0.03
        
        df_bool = filter_frequent_items_matrix(sparse_matrix, item_names, min_item_support=supp_thresh*0.8)
        frequent_itemsets, _, _ = mine_fpgrowth(df_bool, min_support=supp_thresh, max_len=4)
        
        rules = generate_rules(frequent_itemsets, min_confidence=0.3, min_lift=1.2)
        
        top_country_rules = rules.sort_values(by="lift", ascending=False).head(5) if not rules.empty else pd.DataFrame()
        
        summary_list = []
        if not top_country_rules.empty:
            for _, r in top_country_rules.iterrows():
                summary_list.append({
                    "rule": r["rule_str"],
                    "confidence": r["confidence"],
                    "lift": r["lift"]
                })
                
        country_results[country] = {
            "total_baskets": len(baskets),
            "min_support_used": supp_thresh,
            "rules_mined": len(rules),
            "top_5_rules": summary_list
        }
        
    with open(os.path.join(output_dir, "country_segment_analysis.json"), "w") as f:
        json.dump(country_results, f, indent=2)

    logging.info(f"Country segment analysis complete. Summary saved to: {os.path.join(output_dir, 'country_segment_analysis.json')}")
    return country_results


def get_retail_action_plan(top_rules_df):
    """Generate 4 concrete retail business actions."""
    if top_rules_df.empty:
        return []

    top_lift_rules = top_rules_df.sort_values(by="lift", ascending=False).head(5)
    
    actions = [
        {
            "category": "Shelf Co-Placement & Layout Strategy",
            "action": f"Position '{top_lift_rules.iloc[0]['antecedents_str']}' directly adjacent to '{top_lift_rules.iloc[0]['consequents_str']}' in retail display aisles.",
            "rationale": f"High co-occurrence lift of {top_lift_rules.iloc[0]['lift']:.1f}x indicates strong physical impulse purchase correlation."
        },
        {
            "category": "Product Combo Bundling",
            "action": f"Create a packaged bundle featuring '{top_lift_rules.iloc[1]['antecedents_str']}' and '{top_lift_rules.iloc[1]['consequents_str']}' with a 10% promotional bundle discount.",
            "rationale": f"Confidence of {top_lift_rules.iloc[1]['confidence']*100:.1f}% indicates high willingness to buy both items together."
        },
        {
            "category": "Digital Cross-Selling Prompts",
            "action": f"Implement an automated e-commerce cross-sell pop-up: 'Customers who bought {top_lift_rules.iloc[2]['antecedents_str']} also added {top_lift_rules.iloc[2]['consequents_str']} to their cart'.",
            "rationale": f"Lift of {top_lift_rules.iloc[2]['lift']:.1f}x significantly boosts e-commerce Average Order Value (AOV)."
        },
        {
            "category": "Inventory Replenishment & Supply Chain",
            "action": f"Synchronize re-order points for '{top_lift_rules.iloc[0]['antecedents_str']}' and '{top_lift_rules.iloc[0]['consequents_str']}' to prevent stockouts.",
            "rationale": "A stockout in the antecedent product directly depresses sales of the dependent consequent product."
        }
    ]
    return actions


if __name__ == "__main__":
    from src.rule_generator import run_rule_pipeline
    rules, top_lift, _, _ = run_rule_pipeline(min_support=0.02, min_confidence=0.3, min_lift=1.2)
    
    insights = generate_business_insights(top_lift.head(5))
    print("\n--- TRANSLATED BUSINESS INSIGHTS ---")
    for ins in insights:
        print(f"- {ins['insight']}")
        print(f"  --> {ins['actionable_recommendation']}\n")
        
    country_seg = run_country_segment_analysis()
    print("\n--- COUNTRY SEGMENT SUMMARY ---")
    print(json.dumps(country_seg, indent=2))
