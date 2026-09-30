"""
Algorithm Explainer & Simulation Engine for Market Basket Analysis.
Provides step-by-step visual & structural explanations of Apriori vs FP-Growth mechanics.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_apriori_step_explanation():
    """Return step-by-step technical breakdown of Apriori algorithm mechanics."""
    steps = [
        {
            "step": "Step 1: Scan 1 & Frequent 1-Itemsets (L1)",
            "title": "Pass 1 over Database — Calculate Item Frequencies",
            "action": "Scan all transactions, calculate Support for each item, and discard items with Support < min_support.",
            "formula": "L_1 = { i | Support({i}) >= min_support }",
            "complexity": "1 Database Scan"
        },
        {
            "step": "Step 2: Candidate 2-Itemset Generation (C2)",
            "title": "Generate Candidate 2-Itemsets via Self-Join (L1 x L1)",
            "action": "Join frequent 1-itemsets to form pairs. Apply Apriori Pruning Property: any pair containing an infrequent item is pruned.",
            "formula": "C_2 = L_1 ⋈ L_1",
            "complexity": "Combinatorial Candidate Generation"
        },
        {
            "step": "Step 3: Scan 2 & Frequent 2-Itemsets (L2)",
            "title": "Pass 2 over Database — Count C2 Candidate Supports",
            "action": "Scan all transactions a second time to count occurrences of every candidate in C_2. Prune candidates below min_support.",
            "formula": "L_2 = { c ∈ C_2 | Support(c) >= min_support }",
            "complexity": "2nd Database Scan"
        },
        {
            "step": "Step 4: Iterative k-Itemset Mining (Ck -> Lk)",
            "title": "Repeat Candidate Generation & Pruning for k = 3, 4...",
            "action": "Join L_{k-1} to form C_k candidates, scan database for Pass k, and extract L_k until no further candidates exist.",
            "formula": "L_k = Prune(C_k) via Pass k Scan",
            "complexity": "k Full Database Scans"
        }
    ]
    return steps


def get_fpgrowth_step_explanation():
    """Return step-by-step technical breakdown of FP-Growth algorithm mechanics."""
    steps = [
        {
            "step": "Pass 1: Frequency Calculation & Item Sorting",
            "title": "Database Scan 1 — Count Frequencies & Sort Items",
            "action": "Scan transactions once to calculate 1-item supports. Filter items below min_support and sort frequent items in descending order of frequency.",
            "structure": "Header Table (Items sorted by Support)",
            "complexity": "Exactly 1st Database Scan"
        },
        {
            "step": "Pass 2: FP-Tree Construction (Trie Structure)",
            "title": "Database Scan 2 — Construct In-Memory FP-Tree",
            "action": "Scan transactions a second time. Insert sorted transaction items into an FP-Tree (Trie structure). Shared transaction prefixes share tree nodes.",
            "structure": "FP-Tree (Nodes with Item Name, Count, Parent Pointer, Node Links)",
            "complexity": "2nd (and Final) Database Scan"
        },
        {
            "step": "Header Table Link Connection",
            "title": "Link Same-Item Nodes via Linked List Pointers",
            "action": "Connect all tree nodes corresponding to the same product through linked-list pointers originating from the Header Table.",
            "structure": "Header Table -> Linked List of Tree Nodes",
            "complexity": "In-Memory Pointer Assignment"
        },
        {
            "step": "Recursive Tree Mining (No Candidate Generation)",
            "title": "Mine Conditional Pattern Bases & Conditional FP-Trees",
            "action": "Traverse the FP-Tree bottom-up from the Header Table. Construct Conditional Pattern Bases and recursively generate frequent itemsets.",
            "structure": "Conditional Pattern Base -> Conditional FP-Tree",
            "complexity": "0 Candidate Sets Generated!"
        }
    ]
    return steps


def get_algorithm_comparison_matrix():
    """Return detailed comparison matrix between Apriori and FP-Growth."""
    data = [
        {
            "Feature / Metric": "Core Approach",
            "Apriori Algorithm": "Level-wise candidate generation & testing (C_k)",
            "FP-Growth Algorithm": "Divide-and-conquer frequent pattern growth (FP-Tree)",
            "Winner / Advantage": "FP-Growth (No candidate sets)"
        },
        {
            "Feature / Metric": "Database Scans Required",
            "Apriori Algorithm": "k Database Scans (where k = max itemset length)",
            "FP-Growth Algorithm": "Exactly 2 Database Scans total",
            "Winner / Advantage": "FP-Growth (Only 2 Scans)"
        },
        {
            "Feature / Metric": "Candidate Generation (C_k)",
            "Apriori Algorithm": "Generates millions of candidate itemsets (2^M potential)",
            "FP-Growth Algorithm": "ZERO candidate itemsets generated!",
            "Winner / Advantage": "FP-Growth (Eliminates O(2^M) candidate space)"
        },
        {
            "Feature / Metric": "Data Structure Used",
            "Apriori Algorithm": "Relational Arrays / Matrices scanned repeatedly",
            "FP-Growth Algorithm": "Compact Trie Tree (FP-Tree) + Header Table Links",
            "Winner / Advantage": "FP-Growth (Compact Trie)"
        },
        {
            "Feature / Metric": "Performance on Low Support",
            "Apriori Algorithm": "Slow / Memory Bottleneck due to candidate explosion",
            "FP-Growth Algorithm": "Fast & Efficient pattern growth",
            "Winner / Advantage": "FP-Growth (Handles low support)"
        },
        {
            "Feature / Metric": "Vectorized Boolean Variant",
            "Apriori Algorithm": "Extremely fast on dense pre-filtered boolean matrices",
            "FP-Growth Algorithm": "Overhead in DataFrame conversion for small columns",
            "Winner / Advantage": "Apriori (Dense matrix vectorized bitwise operations)"
        }
    ]
    return pd.DataFrame(data)
