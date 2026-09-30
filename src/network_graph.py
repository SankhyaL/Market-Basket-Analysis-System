"""
Product Co-Occurrence Network Graph Generator for Market Basket Analysis.
Constructs network graphs using NetworkX where nodes represent products and edges represent association strength (lift/confidence).
"""

import os
import sys
import logging
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def build_product_network(rules_df, min_lift=2.0, max_edges=40):
    """
    Construct a NetworkX Graph from association rules.
    """
    if rules_df.empty:
        logging.warning("Empty rules DataFrame provided for network graph construction.")
        return nx.DiGraph()

    filtered_rules = rules_df[rules_df["lift"] >= min_lift].sort_values(by="lift", ascending=False).head(max_edges)
    
    G = nx.DiGraph()
    
    for _, row in filtered_rules.iterrows():
        antecedents = row["antecedents_str"]
        consequents = row["consequents_str"]
        lift = float(row["lift"])
        confidence = float(row["confidence"])
        support = float(row["support"])
        
        G.add_node(antecedents, node_type="product")
        G.add_node(consequents, node_type="product")
        G.add_edge(antecedents, consequents, weight=lift, lift=lift, confidence=confidence, support=support)
        
    logging.info(f"Built product network graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G


def plot_network_graph(G, output_path="reports/insights/network_graph.png"):
    """
    Plot and save aesthetic product co-occurrence network visualization.
    """
    if G.number_of_nodes() == 0:
        logging.warning("Graph G has 0 nodes. Skipping network plot.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(14, 10))
    
    # Layout positioning using spring layout
    pos = nx.spring_layout(G, k=0.8, seed=42)
    
    # Node sizing based on degree centrality
    degrees = dict(G.degree())
    node_sizes = [v * 300 + 400 for v in degrees.values()]
    
    # Edge width based on Lift
    edges = G.edges(data=True)
    weights = [d["weight"] for u, v, d in edges]
    max_weight = max(weights) if weights else 1.0
    edge_widths = [((w / max_weight) ** 1.5) * 4 + 1.0 for w in weights]
    
    # Draw network components
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="#3498db", alpha=0.85, edgecolors="#2980b9")
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color="#e74c3c", alpha=0.6, arrowstyle="-|>", arrowsize=15)
    
    # Labels with wrapping/shortening for aesthetic clarity
    labels = {node: node[:25] + "..." if len(node) > 25 else node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_family="sans-serif", font_weight="bold")
    
    plt.title("Product Co-Occurrence & Association Network Graph (Edge Thickness = Lift)", fontsize=14, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logging.info(f"Saved product network graph visualization to: {output_path}")


if __name__ == "__main__":
    from src.rule_generator import run_rule_pipeline
    rules, _, _, _ = run_rule_pipeline(min_support=0.02, min_confidence=0.3, min_lift=1.2)
    G = build_product_network(rules, min_lift=2.0)
    plot_network_graph(G)
