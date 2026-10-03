"""
Enterprise-Grade Market Basket Analytics & Explainable AI (XAI) Intelligence Platform.
Streamlit application featuring Plotly 3D visualizers, dynamic neon glassmorphism UI,
Apriori vs FP-Growth step-by-step algorithm explainer, XAI attributions, and cross-sell engines.
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
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.encoder import load_cleaned_data, create_basket_lists, encode_transactions_sparse
from src.frequent_mining import filter_frequent_items_matrix, mine_fpgrowth, mine_apriori, compare_algorithms
from src.rule_generator import generate_rules, identify_misleading_rules
from src.insights import generate_business_insights, get_retail_action_plan, run_country_segment_analysis
from src.network_graph import build_product_network
from src.xai_explainer import explain_rule_xai, generate_xai_breakdown_table
from src.algo_explainer import get_apriori_step_explanation, get_fpgrowth_step_explanation, get_algorithm_comparison_matrix

# Page Configuration
st.set_page_config(
    page_title="Market Basket AI & XAI Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Ultra-Modern Neon Glassmorphism CSS
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0b0f19 100%);
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Gradient & Glow */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #cbd5e1;
        margin-bottom: 1.5rem;
    }
    
    /* Dynamic Glassmorphic Metric Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 1.4rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 12px 40px rgba(56, 189, 248, 0.25);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 0.3rem;
        font-weight: 700;
    }

    /* Algorithm Card */
    .algo-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        color: #e2e8f0;
    }
    .algo-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 0.5rem;
    }

    /* Role Badges */
    .role-badge-admin {
        background: linear-gradient(90deg, #ef4444, #f97316);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        display: inline-block;
    }
    .role-badge-user {
        background: linear-gradient(90deg, #10b981, #06b6d4);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* --- ENHANCED TAB STYLING (High Visibility) --- */
    div[data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border-radius: 12px !important;
        padding: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        gap: 6px !important;
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    button[data-baseweb="tab"]:hover {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38bdf8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(129, 140, 248, 0.25)) !important;
        color: #38bdf8 !important;
        font-weight: 800 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
        color: inherit !important;
        font-weight: inherit !important;
    }

    /* --- ENHANCED BUTTON STYLING --- */
    .stButton > button, div[data-testid="stButton"] > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover, div[data-testid="stButton"] > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
    .stButton > button:active, div[data-testid="stButton"] > button:active {
        transform: translateY(0px) !important;
    }
    .stButton > button p, div[data-testid="stButton"] > button p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* --- INPUT FIELDS & LABELS --- */
    div[data-baseweb="input"], div[data-baseweb="base-input"], input[type="text"], input[type="password"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #f8fafc !important;
        background-color: transparent !important;
    }
    input::placeholder {
        color: #94a3b8 !important;
    }
    label[data-testid="stWidgetLabel"], .stTextInput label, .stSelectbox label, .stSlider label {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }

    /* --- SELECTBOXES & DROPDOWNS --- */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span {
        color: #f8fafc !important;
    }
    div[data-baseweb="popover"], ul[role="listbox"] {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        color: #f8fafc !important;
    }
    li[role="option"] {
        color: #f8fafc !important;
        background-color: #1e293b !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #334155 !important;
        color: #38bdf8 !important;
    }

    /* --- SIDEBAR STYLING --- */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #cbd5e1 !important;
    }

    /* --- SLIDERS --- */
    div[data-testid="stSlider"] [data-testid="stTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stTickBarMax"],
    div[data-testid="stSlider"] span {
        color: #94a3b8 !important;
    }

    /* --- GENERAL TEXT VISIBILITY --- */
    .stMarkdown, .stMarkdown p, .stCaption, small, p {
        color: #e2e8f0;
    }
    .stCaption, small {
        color: #94a3b8 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
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
    st.markdown('<div class="hero-subtitle">Enterprise Cross-Selling Intelligence & Explainable AI Engine</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="glass-card" style="text-align: left; padding: 2rem;">', unsafe_allow_html=True)
        st.subheader("🔐 Sign In to Analytics Portal")
        
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
            if c_a.button("⚡ Login as Admin Mode", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.session_state.username = "Admin Demo"
                st.rerun()
            if c_u.button("👤 Login as User Mode", use_container_width=True):
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

    with st.spinner("Mining patterns, generating 3D Plotly visualizers & XAI attributions..."):
        rules_df, frequent_itemsets, misleading_df, total_baskets = run_mining_cached(
            df_clean, country_filter, min_support, min_confidence, min_lift, max_len
        )

    # Main Navigation Tabs
    tabs = st.tabs([
        "📊 Executive Dashboard",
        "🌌 Interactive 3D Rule Plotly Visualizer",
        "⚙️ Algorithm Master Class (Apriori vs FP-Growth)",
        "🧠 Explainable AI (XAI) Rule Attribution",
        "🔥 Product Affinity Heatmap Matrix",
        "⚡ Association Rules Explorer",
        "🌐 Product Network Graph",
        "🎯 Cross-Sell Recommender",
        "💡 Strategy Action Plan"
    ])

    # --- TAB 1: EXECUTIVE DASHBOARD ---
    with tabs[0]:
        st.subheader("System Overview & Metric Cards")
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
            st.subheader("Top 15 Products by Purchase Volume")
            top_freq = df_clean["Description"].value_counts().head(15).reset_index()
            top_freq.columns = ["Product", "Volume"]
            fig_freq = px.bar(top_freq, x="Volume", y="Product", orientation="h", color="Volume",
                              color_continuous_scale="Viridis", title="Top Selling Products by Transactions")
            fig_freq.update_layout(template="plotly_dark", height=450, yaxis={"autorange": "reversed"})
            st.plotly_chart(fig_freq, use_container_width=True)

        with c_r:
            st.subheader("Top 15 Products by Generated Revenue (£)")
            df_clean["Revenue"] = df_clean["Quantity"] * df_clean["Price"]
            top_rev = df_clean.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(15).reset_index()
            top_rev.columns = ["Product", "Revenue"]
            fig_rev = px.bar(top_rev, x="Revenue", y="Product", orientation="h", color="Revenue",
                             color_continuous_scale="Magma", title="Top Products by Revenue (£)")
            fig_rev.update_layout(template="plotly_dark", height=450, yaxis={"autorange": "reversed"})
            st.plotly_chart(fig_rev, use_container_width=True)

    # --- TAB 2: INTERACTIVE 3D RULE PLOTLY VISUALIZER ---
    with tabs[1]:
        st.subheader("🌌 Interactive 3D Rule Scatter Plot (Support vs Confidence vs Lift)")
        st.write("Rotate, zoom, and inspect every mined rule in 3D space. X = Support, Y = Confidence, Z = Lift.")
        
        if not rules_df.empty:
            fig_3d = px.scatter_3d(
                rules_df,
                x="support",
                y="confidence",
                z="lift",
                color="lift",
                size="support",
                hover_data=["antecedents_str", "consequents_str"],
                color_continuous_scale="Turbo",
                title="3D Association Rule Topology Map"
            )
            fig_3d.update_layout(template="plotly_dark", height=700)
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.warning("No rules mined to render 3D visualizer.")

    # --- TAB 3: ALGORITHM MASTER CLASS (APRIORI vs FP-GROWTH) ---
    with tabs[2]:
        st.subheader("⚙️ Algorithm Master Class: Apriori vs FP-Growth Under the Hood")
        st.write("Understand the exact step-by-step internal mechanisms of both frequent pattern mining algorithms.")

        comp_matrix = get_algorithm_comparison_matrix()
        st.dataframe(comp_matrix, use_container_width=True)

        a_col1, a_col2 = st.columns(2)
        with a_col1:
            st.markdown("### 🐢 Apriori Step-by-Step Flow")
            ap_steps = get_apriori_step_explanation()
            for step in ap_steps:
                st.markdown(f"""
                <div class="algo-card">
                    <div class="algo-card-title">{step['step']}</div>
                    <p><b>{step['title']}</b></p>
                    <p>• {step['action']}</p>
                    <p><code>Formula: {step['formula']}</code></p>
                    <p><small style="color: #f97316;">Complexity Impact: {step['complexity']}</small></p>
                </div>
                """, unsafe_allow_html=True)

        with a_col2:
            st.markdown("### 🐆 FP-Growth Step-by-Step Flow")
            fp_steps = get_fpgrowth_step_explanation()
            for step in fp_steps:
                st.markdown(f"""
                <div class="algo-card">
                    <div class="algo-card-title">{step['step']}</div>
                    <p><b>{step['title']}</b></p>
                    <p>• {step['action']}</p>
                    <p><code>Structure: {step['structure']}</code></p>
                    <p><small style="color: #10b981;">Complexity Impact: {step['complexity']}</small></p>
                </div>
                """, unsafe_allow_html=True)

    # --- TAB 4: EXPLAINABLE AI (XAI) RULE ATTRIBUTION ---
    with tabs[3]:
        st.subheader("🧠 Explainable AI (XAI) — Feature Attribution & Why Rules Occur")
        st.write("Deconstruct *WHY* the AI model identified a rule by comparing Base Support $P(C)$ against Behavior Boost Gain $+(\text{Confidence} - P(C))$.")

        if not rules_df.empty:
            xai_df = generate_xai_breakdown_table(rules_df.head(15))
            st.dataframe(xai_df, use_container_width=True)

            st.markdown("---")
            st.subheader("📊 Interactive XAI Waterfall Attribution Breakdown")
            selected_rule_idx = st.selectbox("Select Rule to Deconstruct:", range(len(rules_df.head(10))),
                                             format_func=lambda i: rules_df.iloc[i]["rule_str"])
            
            exp_data = explain_rule_xai(rules_df.iloc[selected_rule_idx])
            
            fig_waterfall = go.Figure(go.Waterfall(
                name="XAI Attribution",
                orientation="v",
                measure=["relative", "relative", "total"],
                x=["Base Rate P(C)", "Behavior Boost Gain", "Final Confidence P(C|A)"],
                y=[exp_data["base_probability_pct"], exp_data["confidence_gain_pct"], exp_data["conditional_confidence_pct"]],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": "#ef4444"}},
                increasing={"marker": {"color": "#10b981"}},
                totals={"marker": {"color": "#38bdf8"}}
            ))
            fig_waterfall.update_layout(title=f"XAI Waterfall Attribution for: {exp_data['rule_str']}", template="plotly_dark", height=450)
            st.plotly_chart(fig_waterfall, use_container_width=True)
        else:
            st.warning("No rules available for XAI deconstruction.")

    # --- TAB 5: PRODUCT AFFINITY HEATMAP MATRIX ---
    with tabs[4]:
        st.subheader("🔥 Product Co-Occurrence Affinity Heatmap Matrix")
        st.write("Matrix showing co-occurrence intensity (Lift scores) between top pairs of products.")

        if not rules_df.empty:
            top_pairs_rules = rules_df[rules_df["antecedents_str"].str.find(",") == -1]
            top_pairs_rules = top_pairs_rules[top_pairs_rules["consequents_str"].str.find(",") == -1].head(15)
            
            if not top_pairs_rules.empty:
                pivot_matrix = top_pairs_rules.pivot(index="antecedents_str", columns="consequents_str", values="lift").fillna(0)
                fig_hm = px.imshow(pivot_matrix, color_continuous_scale="Plasma", title="Product Lift Co-Occurrence Matrix")
                fig_hm.update_layout(template="plotly_dark", height=600)
                st.plotly_chart(fig_hm, use_container_width=True)
            else:
                st.info("No 1-to-1 product pairs match current Lift filter for matrix plot.")
        else:
            st.warning("No rules available to build matrix.")

    # --- TAB 6: ASSOCIATION RULES EXPLORER ---
    with tabs[5]:
        st.subheader("⚡ Association Rules Explorer & CSV Exporter")
        if not rules_df.empty:
            sorted_rules = rules_df.sort_values(by="lift", ascending=False)
            st.dataframe(sorted_rules[["rule_str", "support", "confidence", "lift", "conviction", "leverage"]], use_container_width=True)
            csv_data = sorted_rules.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Mined Rules (CSV)", data=csv_data, file_name="mined_association_rules.csv", mime="text/csv")
        if not misleading_df.empty:
            st.subheader("⚠️ Pruned Spurious Rules (Lift ≈ 1.0 Filtered)")
            st.dataframe(misleading_df[["rule_str", "confidence", "consequent support", "lift", "explanation"]], use_container_width=True)

    # --- TAB 7: PRODUCT NETWORK GRAPH ---
    with tabs[6]:
        st.subheader("🌐 Product Co-Occurrence Network Graph")
        if not rules_df.empty:
            min_graph_lift = st.slider("Filter Edges by Min Lift", float(min_lift), 25.0, max(float(min_lift), 2.0), step=0.5)
            G = build_product_network(rules_df, min_lift=min_graph_lift, max_edges=35)
            if G.number_of_nodes() > 0:
                fig, ax = plt.subplots(figsize=(12, 8))
                fig.patch.set_facecolor('#0b0f19')
                ax.set_facecolor('#0b0f19')
                pos = nx.spring_layout(G, k=0.7, seed=42)
                degrees = dict(G.degree())
                node_sizes = [v * 250 + 350 for v in degrees.values()]
                weights = [d["weight"] for u, v, d in G.edges(data=True)]
                max_w = max(weights) if weights else 1.0
                edge_widths = [((w / max_w) ** 1.5) * 3.5 + 1.0 for w in weights]
                
                nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="#38bdf8", alpha=0.85, ax=ax)
                nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color="#c084fc", alpha=0.6, arrowstyle="-|>", arrowsize=14, ax=ax)
                labels = {node: node[:22] + "..." if len(node) > 22 else node for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color="white", font_weight="bold", ax=ax)
                plt.axis("off")
                st.pyplot(fig)

    # --- TAB 8: CROSS-SELL RECOMMENDER ---
    with tabs[7]:
        st.subheader("🎯 Pick a Product — Interactive Cross-Sell Engine")
        catalog = sorted(df_clean["Description"].unique().tolist())
        selected_product = st.selectbox("Target Product in Cart:", catalog, index=0)
        
        if not rules_df.empty:
            matched_rules = rules_df[rules_df["antecedents_str"].str.contains(selected_product, case=False, regex=False)]
            if not matched_rules.empty:
                top_recs = matched_rules.sort_values(by="lift", ascending=False).head(5)
                for idx, row in top_recs.reset_index().iterrows():
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: left; margin-bottom: 1rem;">
                        <h4>🎁 Recommended Cross-Sell #{idx+1}: <span style="color: #38bdf8;">{row['consequents_str']}</span></h4>
                        <p>• <b>Lift Boost:</b> {row['lift']:.2f}x higher likelihood than random chance</p>
                        <p>• <b>Confidence:</b> {row['confidence']*100:.1f}% of target buyers also purchase this item</p>
                        <p>• <b>Action Plan:</b> Display checkout cross-sell banner or 10% combo discount.</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"No direct rules for '{selected_product}' under current thresholds. Try lowering min_support.")

    # --- TAB 9: STRATEGY ACTION PLAN ---
    with tabs[8]:
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
