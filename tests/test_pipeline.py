"""
Unit Tests for Market Basket Analysis Pipeline.
Tests data cleaning, sparse matrix encoding, frequent pattern mining, association rule extraction,
misleading rule identification, and Explainable AI (XAI) rule attributions.
"""

import os
import sys

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
import numpy as np
from scipy import sparse
from src.data_loader import clean_data
from src.encoder import create_basket_lists, encode_transactions_sparse
from src.frequent_mining import filter_frequent_items_matrix, mine_fpgrowth, mine_apriori
from src.rule_generator import generate_rules, identify_misleading_rules
from src.xai_explainer import explain_rule_xai, generate_xai_breakdown_table


@pytest.fixture
def dummy_transactions():
    """Fixture providing dummy raw transaction DataFrame."""
    data = {
        "InvoiceNo": ["1001", "1001", "1002", "1002", "1002", "C1003", "1004", "1004"],
        "StockCode": ["85048", "22041", "85048", "22041", "21232", "85048", "POST", "22041"],
        "Description": ["Product A", "Product B", "Product A", "Product B", "Product C", "Product A", "POSTAGE", "Product B"],
        "Quantity": [5, 2, 1, 3, 10, -1, 1, 4],
        "InvoiceDate": ["2010-12-01 08:26:00"] * 8,
        "Price": [2.5, 1.0, 2.5, 1.0, 4.0, 2.5, 5.0, 1.0],
        "CustomerID": [13085, 13085, 13085, 14000, 14000, 13085, 13085, 15000],
        "Country": ["United Kingdom"] * 8
    }
    return pd.DataFrame(data)


def test_clean_data(dummy_transactions):
    """Test data cleaning logic."""
    cleaned = clean_data(dummy_transactions)
    # 1. Cancelled order C1003 removed
    assert not cleaned["InvoiceNo"].str.startswith("C").any()
    # 2. Non-product stock code 'POST' / 'POSTAGE' removed
    assert not (cleaned["StockCode"] == "POST").any()
    # 3. Descriptions standardized
    assert "PRODUCT A" in cleaned["Description"].values
    # 4. Valid row count
    assert len(cleaned) == 6


def test_encoder_and_basket_creation(dummy_transactions):
    """Test basket grouping and sparse matrix encoding."""
    cleaned = clean_data(dummy_transactions)
    baskets, invoice_ids = create_basket_lists(cleaned)
    assert len(baskets) == 3
    
    sparse_df, sparse_matrix, items = encode_transactions_sparse(baskets)
    assert sparse_matrix.shape[0] == 3
    assert len(items) == 3
    assert "PRODUCT A" in items


def test_frequent_pattern_mining(dummy_transactions):
    """Test FP-Growth and Apriori pattern mining."""
    cleaned = clean_data(dummy_transactions)
    baskets, _ = create_basket_lists(cleaned)
    _, sparse_matrix, items = encode_transactions_sparse(baskets)
    
    df_bool = filter_frequent_items_matrix(sparse_matrix, items, min_item_support=0.1)
    fp_itemsets, _, _ = mine_fpgrowth(df_bool, min_support=0.5, max_len=2)
    ap_itemsets, _, _ = mine_apriori(df_bool, min_support=0.5, max_len=2)
    
    assert len(fp_itemsets) > 0
    assert len(ap_itemsets) == len(fp_itemsets)


def test_rule_generation_and_xai(dummy_transactions):
    """Test association rule extraction and Explainable AI (XAI) attributions."""
    cleaned = clean_data(dummy_transactions)
    baskets, _ = create_basket_lists(cleaned)
    _, sparse_matrix, items = encode_transactions_sparse(baskets)
    
    df_bool = filter_frequent_items_matrix(sparse_matrix, items, min_item_support=0.1)
    frequent_itemsets, _, _ = mine_fpgrowth(df_bool, min_support=0.3, max_len=2)
    
    rules = generate_rules(frequent_itemsets, min_confidence=0.5, min_lift=1.0)
    assert not rules.empty
    
    # Test XAI Explainer
    exp = explain_rule_xai(rules.iloc[0])
    assert "natural_explanation" in exp
    assert "association_strength" in exp
    assert "lift_multiplier" in exp
