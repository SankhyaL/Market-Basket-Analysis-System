"""
Scalable Market Basket Analysis & Explainable AI (XAI) Intelligence Platform.
Streamlit application featuring Admin/User authentication, ultra-modern dynamic UI,
Apriori vs FP-Growth algorithm comparison, XAI rule attributions, and cross-sell lookup tool.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.encoder import load_cleaned_data, create_basket_lists, encode_transactions_sparse
from src.frequent_mining import filter_frequent_items_matrix, mine_fpgrowth, mine_apriori, compare_algorithms
from src.rule_generator import generate_rules, identify_misleading_rules
from src.insights import generate_business_insights, get_retail_action_plan, run_country_segment_analysis
from src.network_graph import build_product_network
from src.xai_explainer import explain_rule_xai, generate_xai_breakdown_table

# Page Configuration
st.set_page_config(
    page_title="Market Basket AI & XAI Cross-Sell Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Ultra-Modern Neon Glassmorphism CSS
st.markdown("""
<style>
    /* Global Background & Typography */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Gradient & Glow */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    
    /* Dynamic Glassmorphic Metric Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.4rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.2);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #f8fafc;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
        font-weight: 600;
    }

    /* XAI Recommendation Card */
    .xai-card {
        background: rgba(15, 23, 42, 0.85);
        border-left: 5px solid #38bdf8;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* Role Badges */
    .role-badge-admin {
        background: linear-gradient(90deg, #ef4444, #f97316);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .role-badge-user {
        background: linear-gradient(90deg, #10b981, #06b6d4);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# Session State Authentication Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Guest"
if "username" not in st.session_state:
    st.session_state.username = ""


@st.cache_data(show_spinner=False)
def get_cached_cleaned_data():
    return load_cleaned_data()


@st.cache_data(show_spinner=False)
def run_mining_cached(df, country_filter, min_support, min_confidence, min_lift, max_len):
    if country_filter != "All Countries":
        filtered_df = df[df["Country"] == country_filter]
    else:
        filtered_df = df

    if filtered_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0

    baskets, _ = create_basket_lists(filtered_df)
    total_baskets = len(baskets)
    
    if total_baskets == 0:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0

    _, sparse_matrix, item_names = encode_transactions_sparse(baskets)
    df_bool = filter_frequent_items_matrix(sparse_matrix, item_names, min_item_support=min_support*0.8)
    
    frequent_itemsets, _, _ = mine_fpgrowth(df_bool, min_support=min_support, max_len=max_len)
    rules = generate_rules(frequent_itemsets, min_confidence=min_confidence, min_lift=min_lift)
    misleading = identify_misleading_rules(frequent_itemsets, min_confidence=min_confidence)
    
    return rules, frequent_itemsets, misleading, total_baskets


def login_screen():
    """Render sleek modern glassmorphism login portal."""
    st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">⚡ Market Basket AI Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Authenticating Portal — Enterprise Cross-Selling Intelligence</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="glass-card" style="text-align: left; padding: 2rem;">', unsafe_allow_html=True)
        st.subheader("🔐 Sign In")
        
        login_tab1, login_tab2 = st.tabs(["🔑 Password Login", "⚡ Quick Demo Access"])
        
        with login_tab1:
            user_input = st.text_input("Username", key="login_user")
            pass_input = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login to Portal", use_container_width=True):
                if user_input.lower() == "admin" and pass_input == "admin123":
                    st.session_state.authenticated = True
                    st.session_state.user_role = "Admin"
                    st.session_state.username = "Administrator"
                    st.rerun()
                elif user_input.lower() == "user" and pass_input == "user123":
                    st.session_state.authenticated = True
                    st.session_state.user_role = "User"
                    st.session_state.username = "Retail Manager"
                    st.rerun()
                else:
                    st.error("Invalid credentials! (Try 'admin'/'admin123' or 'user'/'user123')")

        with login_tab2:
            st.caption("Select a role for immediate access:")
            c_a, c_u = st.columns(2)
            if c_a.button("⚡ Login as Admin", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.session_state.username = "Admin Demo"
                st.rerun()
            if c_u.button("👤 Login as User", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_role = "User"
                st.session_state.username = "User Demo"
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    if not st.session_state.authenticated:
        login_screen()
        return

    # Header Bar
    role_class = "role-badge-admin" if st.session_state.user_role == "Admin" else "role-badge-user"
    
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown('<div class="hero-title">⚡ Market Basket AI & Explainable AI (XAI) Platform</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-subtitle">Logged in as: <b>{st.session_state.username}</b> &nbsp;&nbsp;<span class="{role_class}">{st.session_state.user_role} Mode</span></div>', unsafe_allow_html=True)
    with col_h2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = "Guest"
            st.rerun()

    df_clean = get_cached_cleaned_data()

    # Sidebar Controls (Admin gets full control, User gets view filters)
    st.sidebar.header("⚙️ Mining Controls")
    if st.session_state.user_role == "Admin":
        st.sidebar.info("👑 Admin Permissions: Full Parameter Control Enabled")
    else:
        st.sidebar.success("👤 User Permissions: Standard Recommendation Controls")

    country_options = ["All Countries"] + sorted(df_clean["Country"].unique().tolist())
    country_filter = st.sidebar.selectbox("Filter by Region / Country", country_options, index=0)
    
    min_support = st.sidebar.slider("Min Support (min_support)", 0.005, 0.10, 0.02, step=0.005,
                                    disabled=(st.session_state.user_role != "Admin"))
    min_confidence = st.sidebar.slider("Min Confidence (min_confidence)", 0.10, 0.90, 0.30, step=0.05)
    min_lift = st.sidebar.slider("Min Lift (min_lift)", 1.0, 30.0, 1.2, step=0.5)
    max_len = st.sidebar.slider("Max Itemset Length", 2, 5, 4, disabled=(st.session_state.user_role != "Admin"))

    with st.spinner("Mining patterns & computing XAI attributions..."):
        rules_df, frequent_itemsets, misleading_df, total_baskets = run_mining_cached(
            df_clean, country_filter, min_support, min_confidence, min_lift, max_len
        )

    # Main Navigation Tabs
    tabs = st.tabs([
        "📊 Executive Dashboard",
        "⚖️ Algorithm Comparison (Apriori vs FP-Growth)",
        "🧠 Explainable AI (XAI) Rule Breakdown",
        "⚡ Association Rules Explorer",
        "🌐 Product Network Graph",
        "🎯 Cross-Sell Recommender",
        "💡 Strategy Action Plan"
    ])

    # --- TAB 1: EXECUTIVE DASHBOARD ---
    with tabs[0]:
        st.subheader("System Highlights & Metric Cards")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="glass-card"><div class="metric-value">{total_baskets:,}</div><div class="metric-label">Total Invoices</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="glass-card"><div class="metric-value">{df_clean["Description"].nunique():,}</div><div class="metric-label">Unique Products</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="glass-card"><div class="metric-value">{df_clean["CustomerID"].nunique():,}</div><div class="metric-label">Customers</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="glass-card"><div class="metric-value">{len(frequent_itemsets):,}</div><div class="metric-label">Itemsets Mined</div></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="glass-card"><div class="metric-value">{len(rules_df):,}</div><div class="metric-label">Rules Extracted</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_l, c_r = st.columns(2)
        with c_l:
            st.subheader("Top 15 Best-Selling Products (Volume)")
            top_freq = df_clean["Description"].value_counts().head(15)
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#0f172a')
            ax.set_facecolor('#1e293b')
            sns.barplot(x=top_freq.values, y=top_freq.index, palette="viridis", ax=ax)
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            st.pyplot(fig)

        with c_r:
            st.subheader("Top 15 Products by Revenue (£)")
            df_clean["Revenue"] = df_clean["Quantity"] * df_clean["Price"]
            top_rev = df_clean.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(15)
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#0f172a')
            ax.set_facecolor('#1e293b')
            sns.barplot(x=top_rev.values, y=top_rev.index, palette="magma", ax=ax)
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            st.pyplot(fig)

    # --- TAB 2: ALGORITHM COMPARISON (APRIORI vs FP-GROWTH) ---
    with tabs[1]:
        st.subheader("⚖️ Algorithmic Performance Benchmark: Apriori vs FP-Growth")
        st.write("Comparing candidate generation ($C_k$) versus tree-based pattern growth (FP-Tree).")
        
        bench_data = [
            {"min_support": 0.015, "frequent_itemsets": 493, "apriori_time_sec": 0.187, "fpgrowth_time_sec": 24.27, "fp_ram_mb": 306.79},
            {"min_support": 0.020, "frequent_itemsets": 270, "apriori_time_sec": 0.114, "fpgrowth_time_sec": 9.32, "fp_ram_mb": 306.72},
            {"min_support": 0.030, "frequent_itemsets": 91, "apriori_time_sec": 0.053, "fpgrowth_time_sec": 1.84, "fp_ram_mb": 306.71},
            {"min_support": 0.050, "frequent_itemsets": 20, "apriori_time_sec": 0.025, "fpgrowth_time_sec": 0.52, "fp_ram_mb": 306.71},
        ]
        b_df = pd.DataFrame(bench_data)
        st.dataframe(b_df, use_container_width=True)
        
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.markdown("""
            <div class="glass-card" style="text-align: left;">
                <h4>🐢 Apriori Algorithm</h4>
                <p>• <b>Mechanism:</b> Level-wise search with candidate generation ($C_k$).</p>
                <p>• <b>Scans:</b> Requires $k$ full database scans for length $k$.</p>
                <p>• <b>Bottleneck:</b> Combinatorial candidate explosion at lower support values.</p>
            </div>
            """, unsafe_allow_html=True)
        with b_col2:
            st.markdown("""
            <div class="glass-card" style="text-align: left;">
                <h4>🐆 FP-Growth Algorithm</h4>
                <p>• <b>Mechanism:</b> In-memory trie structure (FP-Tree) with Header Table.</p>
                <p>• <b>Scans:</b> Exactly <b>2 database scans</b> total.</p>
                <p>• <b>Advantage:</b> Zero candidate generation ($C_k$), scaling seamlessly to big data.</p>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 3: EXPLAINABLE AI (XAI) RULE BREAKDOWN ---
    with tabs[2]:
        st.subheader("🧠 Explainable AI (XAI) — Rule Attribution & Breakdown")
        st.write("Understand *WHY* the AI model generated each recommendation by decomposing Lift into Base Probability $P(C)$ and Behavior Boost Gain.")
        
        if not rules_df.empty:
            xai_df = generate_xai_breakdown_table(rules_df.head(15))
            st.dataframe(xai_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🔍 Deep-Dive XAI Rule Explainer")
            selected_rule_idx = st.selectbox("Select Rule to Explain in Plain English:", range(len(rules_df.head(10))),
                                             format_func=lambda i: rules_df.iloc[i]["rule_str"])
            
            exp_data = explain_rule_xai(rules_df.iloc[selected_rule_idx])
            
            st.markdown(f"""
            <div class="xai-card">
                <h3>Rule: <span style="color: #38bdf8;">{exp_data['rule_str']}</span></h3>
                <p style="font-size: 1.1rem;">{exp_data['natural_explanation']}</p>
                <br/>
                <div style="display: flex; justify-content: space-around;">
                    <div><b>Base Rate P(C):</b> {exp_data['base_probability_pct']}%</div>
                    <div><b>Confidence P(C|A):</b> {exp_data['conditional_confidence_pct']}%</div>
                    <div><b>XAI Boost Gain:</b> <span style="color: #10b981;">+{exp_data['confidence_gain_pct']}%</span></div>
                    <div><b>Lift Score:</b> <span style="color: #c084fc;">{exp_data['lift_multiplier']}x</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No rules mined to perform XAI breakdown.")

    # --- TAB 4: ASSOCIATION RULES EXPLORER ---
    with tabs[3]:
        st.subheader("⚡ Interactive Association Rules Explorer")
        st.write(f"Mined **{len(rules_df):,}** association rules.")
        if not rules_df.empty:
            sorted_rules = rules_df.sort_values(by="lift", ascending=False)
            st.dataframe(sorted_rules[["rule_str", "support", "confidence", "lift", "conviction", "leverage"]], use_container_width=True)
            csv_data = sorted_rules.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Association Rules (CSV)", data=csv_data, file_name="mined_association_rules.csv", mime="text/csv")
        
        if not misleading_df.empty:
            st.subheader("⚠️ Spurious / Misleading Rules (Lift ≈ 1.0 Pruned)")
            st.dataframe(misleading_df[["rule_str", "confidence", "consequent support", "lift", "explanation"]], use_container_width=True)

    # --- TAB 5: PRODUCT NETWORK GRAPH ---
    with tabs[4]:
        st.subheader("🌐 Product Co-Occurrence Network Graph")
        if not rules_df.empty:
            min_graph_lift = st.slider("Filter Edges by Min Lift", float(min_lift), 25.0, max(float(min_lift), 2.0), step=0.5)
            G = build_product_network(rules_df, min_lift=min_graph_lift, max_edges=35)
            if G.number_of_nodes() > 0:
                fig, ax = plt.subplots(figsize=(12, 8))
                fig.patch.set_facecolor('#0f172a')
                ax.set_facecolor('#0f172a')
                pos = nx.spring_layout(G, k=0.7, seed=42)
                degrees = dict(G.degree())
                node_sizes = [v * 250 + 350 for v in degrees.values()]
                weights = [d["weight"] for u, v, d in G.edges(data=True)]
                max_w = max(weights) if weights else 1.0
                edge_widths = [((w / max_w) ** 1.5) * 3.5 + 1.0 for w in weights]
                
                nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="#38bdf8", alpha=0.85, ax=ax)
                nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color="#ec4899", alpha=0.6, arrowstyle="-|>", arrowsize=14, ax=ax)
                labels = {node: node[:22] + "..." if len(node) > 22 else node for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color="white", font_weight="bold", ax=ax)
                plt.axis("off")
                st.pyplot(fig)

    # --- TAB 6: CROSS-SELL RECOMMENDER ---
    with tabs[5]:
        st.subheader("🎯 Pick a Product — Interactive Cross-Sell Engine")
        catalog = sorted(df_clean["Description"].unique().tolist())
        selected_product = st.selectbox("Target Product in Cart:", catalog, index=0)
        
        if not rules_df.empty:
            matched_rules = rules_df[rules_df["antecedents_str"].str.contains(selected_product, case=False, regex=False)]
            if not matched_rules.empty:
                top_recs = matched_rules.sort_values(by="lift", ascending=False).head(5)
                for idx, row in top_recs.reset_index().iterrows():
                    st.markdown(f"""
                    <div class="xai-card">
                        <h4>🎁 Recommended Cross-Sell #{idx+1}: <span style="color: #38bdf8;">{row['consequents_str']}</span></h4>
                        <p>• <b>Lift Boost:</b> {row['lift']:.2f}x higher likelihood than random chance</p>
                        <p>• <b>Confidence:</b> {row['confidence']*100:.1f}% of target buyers also purchase this item</p>
                        <p>• <b>Action Plan:</b> Display checkout cross-sell banner or 10% combo discount.</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"No direct rules for '{selected_product}' under current thresholds. Try lowering min_support.")

    # --- TAB 7: STRATEGY ACTION PLAN ---
    with tabs[6]:
        st.subheader("💡 Concrete Supermarket Strategy Actions")
        if not rules_df.empty:
            actions = get_retail_action_plan(rules_df)
            for idx, act in enumerate(actions, 1):
                st.markdown(f"""
                <div class="glass-card" style="text-align: left; margin-bottom: 1rem;">
                    <h3>Strategy #{idx}: {act['category']}</h3>
                    <p><b>Action:</b> {act['action']}</p>
                    <p><b>Data Rationale:</b> {act['rationale']}</p>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
