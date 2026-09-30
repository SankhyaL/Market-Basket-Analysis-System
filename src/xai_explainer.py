"""
Explainable AI (XAI) Module for Market Basket Analysis.
Decomposes association rules into interpretable component contributions
(Base Support, Antecedent Boost, Confidence Gain, and Lift Multipliers).
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def explain_rule_xai(rule_row):
    """
    Decompose single association rule into Explainable AI (XAI) feature attribution.
    """
    ant = rule_row["antecedents_str"]
    cons = rule_row["consequents_str"]
    
    supp_a = float(rule_row.get("antecedent support", 0.05))
    supp_c = float(rule_row.get("consequent support", 0.05))
    supp_rule = float(rule_row["support"])
    conf = float(rule_row["confidence"])
    lift = float(rule_row["lift"])
    leverage = float(rule_row.get("leverage", supp_rule - supp_a * supp_c))
    
    # Base rate vs Boosted rate
    base_prob_pct = supp_c * 100
    conf_pct = conf * 100
    boost_gain_pct = conf_pct - base_prob_pct
    relative_boost = (conf / max(supp_c, 0.0001))
    
    # Interpretable Natural Language Explanation
    if relative_boost >= 15.0:
        strength = "CRITICAL / ULTRA-STRONG"
        badge_color = "#e74c3c"
    elif relative_boost >= 5.0:
        strength = "VERY STRONG"
        badge_color = "#e67e22"
    elif relative_boost >= 1.5:
        strength = "MODERATE POSITIVE"
        badge_color = "#2ecc71"
    else:
        strength = "WEAK / SPURIOUS"
        badge_color = "#95a5a6"
        
    summary_explanation = (
        f"Without knowing anything about the cart, any customer has a <b>{base_prob_pct:.1f}%</b> base chance of buying <i>'{cons}'</i>. "
        f"However, when the customer adds <i>'{ant}'</i> to their cart, their probability jumps to <b>{conf_pct:.1f}%</b>. "
        f"This represents an absolute confidence gain of <b>+{boost_gain_pct:.1f}%</b> and a <b>{relative_boost:.1f}x Lift boost</b>."
    )
    
    waterfall_factors = [
        {"factor": f"Base Probability of '{cons}'", "value": round(base_prob_pct, 2), "unit": "%", "type": "baseline"},
        {"factor": f"Behavioral Lift Boost from '{ant}'", "value": round(boost_gain_pct, 2), "unit": "%", "type": "boost"},
        {"factor": "Final Conditional Confidence", "value": round(conf_pct, 2), "unit": "%", "type": "total"},
    ]
    
    return {
        "rule_str": rule_row.get("rule_str", f"{ant} ==> {cons}"),
        "antecedent": ant,
        "consequent": cons,
        "base_probability_pct": round(base_prob_pct, 2),
        "conditional_confidence_pct": round(conf_pct, 2),
        "confidence_gain_pct": round(boost_gain_pct, 2),
        "lift_multiplier": round(lift, 2),
        "leverage": round(leverage, 4),
        "association_strength": strength,
        "badge_color": badge_color,
        "natural_explanation": summary_explanation,
        "waterfall_factors": waterfall_factors
    }


def generate_xai_breakdown_table(rules_df):
    """Generate XAI explanation table for a DataFrame of rules."""
    if rules_df.empty:
        return pd.DataFrame()
        
    xai_rows = []
    for _, row in rules_df.iterrows():
        exp = explain_rule_xai(row)
        xai_rows.append({
            "Rule": exp["rule_str"],
            "Antecedent": exp["antecedent"],
            "Consequent": exp["consequent"],
            "Base Probability P(C)": f"{exp['base_probability_pct']}%",
            "Confidence P(C|A)": f"{exp['conditional_confidence_pct']}%",
            "XAI Boost Gain": f"+{exp['confidence_gain_pct']}%",
            "Lift Multiplier": f"{exp['lift_multiplier']}x",
            "Strength Rating": exp["association_strength"]
        })
    return pd.DataFrame(xai_rows)


if __name__ == "__main__":
    dummy_rule = {
        "antecedents_str": "PINK REGENCY TEACUP AND SAUCER",
        "consequents_str": "GREEN REGENCY TEACUP AND SAUCER",
        "antecedent support": 0.026,
        "consequent support": 0.034,
        "support": 0.0216,
        "confidence": 0.834,
        "lift": 24.59,
        "leverage": 0.0207
    }
    exp = explain_rule_xai(dummy_rule)
    print("\n--- XAI EXPLAINER PREVIEW ---")
    print(f"Strength: {exp['association_strength']}")
    print(f"Explanation: {exp['natural_explanation']}")
