"""
Comprehensive PDF Generator for Market Basket Analysis Project Proposal using ReportLab.
Includes 100% complete text, formulas, technical tables, risk matrices, milestones, and references.
Authors: Tanaya Salunke & Sankhya Londhe
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas for adding page numbers and running header/footer dynamically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#7F8C8D"))
        
        # Header (Page 2+)
        if self._pageNumber > 1:
            self.drawString(45, letter[1] - 30, "PROJECT PROPOSAL: SCALABLE MARKET BASKET ANALYSIS SYSTEM")
            self.drawRightString(letter[0] - 45, letter[1] - 30, "TANAYA SALUNKE & SANKHYA LONDHE")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, letter[1] - 34, letter[0] - 45, letter[1] - 34)
            
        # Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 38, letter[0] - 45, 38)
        
        self.setFont("Helvetica", 8)
        self.drawString(45, 26, "Honors Project Proposal | Department of Computer Science")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 45, 26, page_text)
        self.restoreState()


def create_comprehensive_proposal_pdf(output_filename="reports/Project_Proposal_Market_Basket_Analysis.pdf"):
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1B365D")    # Deep Navy
    c_secondary = colors.HexColor("#2980B9")  # Ocean Blue
    c_dark = colors.HexColor("#2C3E50")       # Dark Charcoal Text
    c_light = colors.HexColor("#F8F9FA")      # Off-white background
    c_accent = colors.HexColor("#D35400")     # Warm accent

    # Custom Typography
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=c_secondary,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_block_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_style = ParagraphStyle(
        "TableCell", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=c_dark
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold", parent=table_cell_style, fontName="Helvetica-Bold"
    )
    table_header_style = ParagraphStyle(
        "TableHeader", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white
    )

    story = []

    # Banner & Title
    story.append(Paragraph("PROJECT PROPOSAL DOCUMENT", subtitle_style))
    story.append(Paragraph("Scalable Market Basket Analysis & Cross-Selling Intelligence System", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=4, spaceAfter=10))

    meta_data = [
        [Paragraph("<b>Project Team / Authors:</b>", body_style), Paragraph("<b>Tanaya Salunke</b> & <b>Sankhya Londhe</b>", body_style)],
        [Paragraph("<b>Academic Context:</b>", body_style), Paragraph("Final Year Honors Project Proposal | Department of Computer Science", body_style)],
        [Paragraph("<b>Domain & Field:</b>", body_style), Paragraph("Data Science, Data Mining, Machine Learning, & Retail Business Analytics", body_style)],
        [Paragraph("<b>Benchmark Dataset:</b>", body_style), Paragraph("Online Retail II Dataset (1,067,371 Raw Records, 2009–2011)", body_style)],
        [Paragraph("<b>Proposal Date:</b>", body_style), Paragraph("September 2026", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[130, 392])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "In contemporary retail and e-commerce environments, massive volumes of transaction logs are generated daily. "
        "Uncovering implicit associations between products purchased together provides critical commercial leverage for "
        "optimizing store layouts, organizing digital cross-selling prompts, designing promotional bundles, and managing inventory replenishment.",
        body_style
    ))
    story.append(Paragraph(
        "This project proposes a scalable, end-to-end <b>Market Basket Analysis (MBA)</b> and Product Cross-Selling Intelligence platform "
        "authored by <b>Tanaya Salunke</b> and <b>Sankhya Londhe</b>. Operating on the benchmark <b>Online Retail II</b> dataset "
        "(containing over 1.06 million transaction rows across 2009–2011), the system ingests raw transaction data, performs rigorous data hygiene, "
        "encodes transactions using memory-efficient sparse boolean matrices, benchmarks frequent pattern mining algorithms "
        "(<b>Apriori vs. FP-Growth</b>), extracts statistical association rules, filters out misleading spurious correlations, and translates mined patterns into actionable retail business strategies.",
        body_style
    ))
    story.append(Paragraph(
        "Furthermore, the system delivers an interactive <b>Streamlit Web Application</b> for real-time rule exploration and product cross-sell recommendations, "
        "alongside an <b>out-of-core batch processing architecture</b> and <b>PySpark FP-Growth reference integration</b> for multi-terabyte dataset scaling.",
        body_style
    ))

    # 2. Problem Statement & Motivation
    story.append(Paragraph("2. Problem Statement & Motivation", h1_style))
    story.append(Paragraph("2.1 Problem Statement", h2_style))
    story.append(Paragraph("Retail businesses collect vast amounts of point-of-sale (POS) and online transaction data, yet frequently fail to extract actionable product co-occurrence patterns. Key operational challenges include:", body_style))
    story.append(Paragraph("1. <b>Product Placement Inefficiencies:</b> Inability to identify which products drive impulse co-purchases, leading to sub-optimal aisle and shelf layouts.", bullet_style))
    story.append(Paragraph("2. <b>Ineffective Cross-Selling:</b> E-commerce platforms display generic or static product recommendations rather than data-driven 'Frequently Bought Together' pairs.", bullet_style))
    story.append(Paragraph("3. <b>Memory Bottlenecks in Association Mining:</b> Standard dense multi-hot encoding of high-cardinality retail catalogs leads to severe memory exhaustion (O(N × M) RAM consumption).", bullet_style))
    story.append(Paragraph("4. <b>Algorithmic Inefficiencies at Scale:</b> Traditional algorithms like Apriori suffer from combinatorial candidate itemset generation (C_k) and repeated database scans when candidate support thresholds are lowered.", bullet_style))
    story.append(Paragraph("5. <b>Spurious / Misleading Rules:</b> Naive association rule mining often surfaces rules with high confidence but low lift (Lift ≈ 1.0), misleading retailers into bundling products that customers purchase independently anyway.", bullet_style))

    story.append(Paragraph("2.2 Motivation", h2_style))
    story.append(Paragraph(
        "By building a scalable, automated pipeline that addresses memory bottlenecks, prunes misleading rules, benchmarks algorithm efficiency, "
        "and presents insights visually via a web application, this project bridges the gap between complex pattern mining theory and real-world retail decision-making.",
        body_style
    ))

    # 3. Project Objectives & Scope
    story.append(Paragraph("3. Project Objectives & Scope", h1_style))
    story.append(Paragraph("3.1 Primary Objectives", h2_style))
    story.append(Paragraph("• <b>Data Ingestion & Hygiene Engine:</b> Build an automated cleaner to filter returns/cancellations (InvoiceNo starting with 'C'), zero/negative quantities and prices, and non-product service charges (POSTAGE, MANUAL, BANK CHARGES).", bullet_style))
    story.append(Paragraph("• <b>Memory-Efficient Encoding:</b> Group transactions into invoice baskets and construct SciPy sparse boolean matrices (csr_matrix), achieving >95% matrix sparsity and >90% RAM footprint reduction.", bullet_style))
    story.append(Paragraph("• <b>Algorithmic Benchmarking:</b> Implement and compare Apriori (mlxtend.apriori) and FP-Growth (mlxtend.fpgrowth) across multiple minimum support thresholds (min_support ∈ {0.015, 0.02, 0.03, 0.05}) in terms of runtime execution (seconds), peak RAM footprint (MB), and itemset yield.", bullet_style))
    story.append(Paragraph("• <b>Rule Mining & Misleading Rule Pruning:</b> Compute Support, Confidence, Lift, Leverage, and Conviction for all candidate rules. Detect and flag misleading rules (Lift < 1.2).", bullet_style))
    story.append(Paragraph("• <b>Business Insight & Network Graph Layer:</b> Build NetworkX product co-occurrence graphs, execute regional segment analysis (UK, Germany, France, EIRE), and formulate concrete retail action plans.", bullet_style))
    story.append(Paragraph("• <b>Out-of-Core Scalability & PySpark Architecture:</b> Develop a chunked batch processor (50,000-row chunks) and map distributed FP-Growth execution to Apache Spark (pyspark.ml.fpm.FPGrowth).", bullet_style))
    story.append(Paragraph("• <b>Interactive Web Application:</b> Deploy a Streamlit dashboard featuring parameter sliders, sortable rule tables, CSV export, network visualizer, and a product cross-sell recommendation lookup tool.", bullet_style))
    story.append(Paragraph("• <b>Testing & Quality Assurance:</b> Implement unit tests using pytest to ensure 100% verification across all pipeline stages.", bullet_style))

    story.append(Paragraph("3.2 Scope Boundary", h2_style))
    story.append(Paragraph("• <b>In-Scope:</b> Transaction-level market basket association mining, sparse matrix encoding, Apriori vs. FP-Growth benchmarking, rule filtering, network graph generation, regional analysis, Streamlit app, out-of-core batching, and PySpark reference module.", bullet_style))
    story.append(Paragraph("• <b>Out-of-Scope:</b> Real-time stream processing (e.g., Apache Kafka live event streaming) and customer RFM demographic modeling.", bullet_style))

    # 4. Theoretical Background & Methodology
    story.append(Paragraph("4. Theoretical Background & Mathematical Methodology", h1_style))
    story.append(Paragraph("4.1 Association Rule Metrics", h2_style))
    story.append(Paragraph("Given a transaction set T and itemsets A (antecedent) and C (consequent):", body_style))
    story.append(Paragraph("1. <b>Support (S):</b> Measures rule frequency across all transactions:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Support(A → C) = P(A ∩ C) = Count(A ∪ C) / |T|</b>", bullet_style))
    story.append(Paragraph("2. <b>Confidence (C):</b> Measures conditional probability of purchasing C given A:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Confidence(A → C) = P(C | A) = Support(A ∪ C) / Support(A)</b>", bullet_style))
    story.append(Paragraph("3. <b>Lift (L):</b> Measures how much more often A and C occur together than expected if independent:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Lift(A → C) = P(A ∩ C) / (P(A) · P(C)) = Confidence(A → C) / Support(C)</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;• Lift > 1.0: Positive co-occurrence association.<br/>&nbsp;&nbsp;&nbsp;&nbsp;• Lift = 1.0: Statistical independence (spurious association).<br/>&nbsp;&nbsp;&nbsp;&nbsp;• Lift < 1.0: Negative correlation.", bullet_style))
    story.append(Paragraph("4. <b>Leverage:</b> Difference between observed joint support and expected independent support:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Leverage(A → C) = Support(A ∪ C) - Support(A) · Support(C)</b>", bullet_style))
    story.append(Paragraph("5. <b>Conviction:</b> Ratio of expected frequency of incorrect prediction to observed incorrect prediction:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Conviction(A → C) = (1 - Support(C)) / (1 - Confidence(A → C))</b>", bullet_style))

    story.append(Paragraph("4.2 Algorithm Comparison: Apriori vs. FP-Growth", h2_style))
    story.append(Paragraph("• <b>Apriori Algorithm:</b> Uses level-wise candidate generation (C_k) and candidate pruning based on the Apriori property (all non-empty subsets of a frequent itemset must also be frequent). Requires k database passes for itemsets of length k.", bullet_style))
    story.append(Paragraph("• <b>FP-Growth Algorithm:</b> Uses a compact FP-Tree (Frequent Pattern Tree) trie structure. Encodes transactions in 2 database passes and mines frequent patterns by constructing conditional FP-trees without candidate generation.", bullet_style))

    # 5. Proposed System Architecture & Technical Modules
    story.append(Paragraph("5. Proposed System Architecture & Technical Modules", h1_style))
    
    arch_table_data = [
        [Paragraph("Pipeline Stage", table_header_style), Paragraph("Technical Module / File", table_header_style), Paragraph("Functional Description & Output", table_header_style)],
        [Paragraph("<b>Stage 1: Hygiene</b>", table_cell_bold), Paragraph("<code>src/data_loader.py</code>", table_cell_style), Paragraph("Cleans raw Excel, filters returns/fees. Output: 1,036,154 clean records.", table_cell_style)],
        [Paragraph("<b>Stage 2: Encoding</b>", table_cell_bold), Paragraph("<code>src/encoder.py</code>", table_cell_style), Paragraph("Groups baskets by InvoiceNo into CSR sparse matrix. 99.53% sparsity.", table_cell_style)],
        [Paragraph("<b>Stage 3: Mining</b>", table_cell_bold), Paragraph("<code>src/frequent_mining.py</code>", table_cell_style), Paragraph("Apriori vs FP-Growth runtime and memory benchmark engine.", table_cell_style)],
        [Paragraph("<b>Stage 4: Rules</b>", table_cell_bold), Paragraph("<code>src/rule_generator.py</code>", table_cell_style), Paragraph("Extracts rules (Support, Conf, Lift), filters misleading Lift ≈ 1.0 rules.", table_cell_style)],
        [Paragraph("<b>Stage 5: Insights</b>", table_cell_bold), Paragraph("<code>src/insights.py</code><br/><code>src/network_graph.py</code>", table_cell_style), Paragraph("Translates rules to business text, runs UK/DE/FR/IE segment mining, builds NetworkX graph.", table_cell_style)],
        [Paragraph("<b>Stage 6: Scalability</b>", table_cell_bold), Paragraph("<code>src/scalability.py</code><br/><code>src/pyspark_fpgrowth.py</code>", table_cell_style), Paragraph("Out-of-core 50k-row batching engine & PySpark MLlib distributed architecture.", table_cell_style)],
        [Paragraph("<b>Stage 7: Web UI</b>", table_cell_bold), Paragraph("<code>app/streamlit_app.py</code>", table_cell_style), Paragraph("Interactive Streamlit dashboard with cross-sell recommendation lookup.", table_cell_style)]
    ]
    t_arch = Table(arch_table_data, colWidths=[100, 140, 282])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_arch)

    # 6. Implementation Stack & Tools
    story.append(Paragraph("6. Implementation Stack & Tools", h1_style))
    tools_table_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Component / Tool", table_header_style), Paragraph("Rationale & Use Case", table_header_style)],
        [Paragraph("<b>Language & Env</b>", table_cell_bold), Paragraph("Python 3.9, PyYaml", table_cell_style), Paragraph("Core execution environment & central configuration file (config.yaml).", table_cell_style)],
        [Paragraph("<b>Data Processing</b>", table_cell_bold), Paragraph("Pandas 2.3, SciPy 1.13, NumPy 2.0", table_cell_style), Paragraph("Out-of-core DataFrames, CSV/Parquet chunking, & csr_matrix sparse encoding.", table_cell_style)],
        [Paragraph("<b>Pattern Mining</b>", table_cell_bold), Paragraph("Mlxtend 0.23, PyFPGrowth 1.0", table_cell_style), Paragraph("Apriori & FP-Growth itemset mining, association rule extraction.", table_cell_style)],
        [Paragraph("<b>Graph & Viz</b>", table_cell_bold), Paragraph("NetworkX 3.2, Matplotlib 3.9, Seaborn 0.13", table_cell_style), Paragraph("Product co-occurrence graph layout, EDA histograms & bar charts.", table_cell_style)],
        [Paragraph("<b>Distributed Scale</b>", table_cell_bold), Paragraph("Apache Spark / PySpark MLlib", table_cell_style), Paragraph("PySpark pyspark.ml.fpm.FPGrowth cluster scaling reference mapping.", table_cell_style)],
        [Paragraph("<b>Interactive Web UI</b>", table_cell_bold), Paragraph("Streamlit 1.50", table_cell_style), Paragraph("Interactive web app with sidebar controls, sortable tables, & recommender lookup.", table_cell_style)],
        [Paragraph("<b>Testing & QA</b>", table_cell_bold), Paragraph("Pytest 8.4", table_cell_style), Paragraph("Unit testing framework for data hygiene, encoding, mining, and rule generation.", table_cell_style)]
    ]
    t_tools = Table(tools_table_data, colWidths=[100, 140, 282])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_tools)

    # 7. Work Plan & Phase-Wise Milestones
    story.append(Paragraph("7. Work Plan & Phase-Wise Milestones", h1_style))
    story.append(Paragraph("• <b>Phase 1: Environment Setup & Project Layout (Segment 1)</b> — Directory structure, virtual environment, dependencies, config.yaml.", bullet_style))
    story.append(Paragraph("• <b>Phase 2: Data Ingestion & Hygiene Pipeline (Segment 2)</b> — Cancellation filtering, text standardization, Parquet/CSV output.", bullet_style))
    story.append(Paragraph("• <b>Phase 3: Transaction Encoding & EDA (Segment 3)</b> — Sparse matrix creation, basket size stats, EDA visualizations.", bullet_style))
    story.append(Paragraph("• <b>Phase 4: Frequent Pattern Mining Benchmark (Segment 4)</b> — Apriori vs. FP-Growth benchmarking across min_supports.", bullet_style))
    story.append(Paragraph("• <b>Phase 5: Association Rule Generation & Pruning (Segment 5)</b> — Rule extraction, Lift/Confidence sorting, misleading rule detection.", bullet_style))
    story.append(Paragraph("• <b>Phase 6: Business Insights & Network Graph Layer (Segment 6)</b> — NetworkX visualization, regional country analysis (UK, DE, FR, IE).", bullet_style))
    story.append(Paragraph("• <b>Phase 7: Out-of-Core Scalability & PySpark Architecture (Segment 7)</b> — 50,000-row chunk processor, StageProfiler, PySpark FPGrowth module.", bullet_style))
    story.append(Paragraph("• <b>Phase 8: Streamlit Interactive Web Application (Segment 8)</b> — Web app with parameter sliders, rule explorer, & cross-sell lookup tool.", bullet_style))
    story.append(Paragraph("• <b>Phase 9: Final Reporting & Synthesis (Segment 9)</b> — Comprehensive markdown executive report (reports/final_report.md).", bullet_style))
    story.append(Paragraph("• <b>Phase 10: Testing, Packaging, & Documentation (Segment 10)</b> — Pytest test suite, main.py CLI runner, README.md setup guide.", bullet_style))

    # 8. Expected Deliverables & Outcomes
    story.append(Paragraph("8. Expected Deliverables & Outcomes", h1_style))
    story.append(Paragraph("1. <b>Cleaned Transactions Dataset:</b> Processed Parquet & CSV tables (1,036,154 records, 39,517 invoices).", bullet_style))
    story.append(Paragraph("2. <b>Modular Python Source Code:</b> Structured codebase in src/ (data_loader, encoder, eda, frequent_mining, rule_generator, network_graph, insights, scalability, pyspark_fpgrowth).", bullet_style))
    story.append(Paragraph("3. <b>Algorithmic Benchmark Metrics:</b> Empirical comparison CSV tables and charts detailing Apriori vs. FP-Growth execution runtimes and memory footprints across support values.", bullet_style))
    story.append(Paragraph("4. <b>Business Strategy & Network Visualizations:</b> High-resolution product co-occurrence network graphs and regional purchasing segment profiles (reports/insights/).", bullet_style))
    story.append(Paragraph("5. <b>Interactive Web Dashboard:</b> Production-ready Streamlit app (app/streamlit_app.py) for live parameter tuning and cross-sell recommendation lookup.", bullet_style))
    story.append(Paragraph("6. <b>Out-of-Core Engine & PySpark Module:</b> Scalability module capable of processing 1M+ transaction rows under an 800 MB RAM budget.", bullet_style))
    story.append(Paragraph("7. <b>Automated Test Suite & CLI Runner:</b> pytest test suite (tests/test_pipeline.py) passing with 100% success rate and single CLI entry point (main.py).", bullet_style))
    story.append(Paragraph("8. <b>Final Technical Report & README:</b> Full documentation in reports/final_report.md and README.md.", bullet_style))

    # 9. Risks, Limitations, & Future Extensions
    story.append(Paragraph("9. Risks, Limitations, & Future Extensions", h1_style))
    story.append(Paragraph("9.1 Risk & Mitigation Plan", h2_style))
    story.append(Paragraph("• <b>Risk 1: Combinatorial Memory Explosion at Low Support Values.</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;<i>Mitigation:</i> Sparse matrix encoding (csr_matrix), item-support pre-filtering, and max_len=4 constraints prevent out-of-memory errors.", bullet_style))
    story.append(Paragraph("• <b>Risk 2: Spurious Rules (High Confidence, Low Lift).</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;<i>Mitigation:</i> Automated filtering prunes all candidate rules with Lift < 1.2.", bullet_style))

    story.append(Paragraph("9.2 Future Extensions", h2_style))
    story.append(Paragraph("1. <b>Multiple Minimum Item Supports (MSApriori):</b> Assigning custom support thresholds to rare, high-value products to prevent undersampling.", bullet_style))
    story.append(Paragraph("2. <b>Temporal & Seasonal Association Mining:</b> Incorporating timestamp seasonality to extract time-varying purchase patterns (e.g., Christmas vs. Summer baskets).", bullet_style))
    story.append(Paragraph("3. <b>High-Utility Itemset Mining (HUIM):</b> Factoring item profit margins into itemset scoring to prioritize profit-maximizing bundles over volume-maximizing bundles.", bullet_style))

    # 10. References
    story.append(Paragraph("10. References", h1_style))
    story.append(Paragraph("1. Agrawal, R., & Srikant, R. (1994). <i>Fast Algorithms for Mining Association Rules in Large Databases</i>. Proceedings of the 20th International Conference on Very Large Data Bases (VLDB), 487–499.", bullet_style))
    story.append(Paragraph("2. Han, J., Pei, J., & Yin, Y. (2000). <i>Mining Frequent Patterns without Candidate Generation</i>. ACM SIGMOD Record, 29(2), 1–12.", bullet_style))
    story.append(Paragraph("3. Chen, D., Sain, S. L., & Guo, K. (2012). <i>Data mining for the online retail industry: Implicit association rule mining</i>. Journal of Database Marketing & Customer Strategy Management, 19(3), 197–208.", bullet_style))
    story.append(Paragraph("4. Raschka, S. (2018). <i>MLxtend: Providing machine learning and data science utilities and extensions to Python's scientific computing stack</i>. Journal of Open Source Software, 3(24), 638.", bullet_style))
    story.append(Paragraph("5. UCI Machine Learning Repository. <i>Online Retail II Data Set</i>. Available at: https://archive.ics.uci.edu/ml/datasets/Online+Retail+II", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated complete comprehensive proposal PDF: {output_filename}")


if __name__ == "__main__":
    create_comprehensive_proposal_pdf()
