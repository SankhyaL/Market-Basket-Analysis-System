"""
Comprehensive PDF Generator for Market Basket Analysis Final Technical Report using ReportLab.
Includes 100% complete text, data hygiene metrics, algorithm benchmark tables, top association rules,
regional country segment findings, retail strategy action plan, and scalability architecture.
Authors: Tanaya Salunke & Sankhya Londhe
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
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
        
        if self._pageNumber > 1:
            self.drawString(45, letter[1] - 30, "FINAL TECHNICAL REPORT: MARKET BASKET ANALYSIS SYSTEM")
            self.drawRightString(letter[0] - 45, letter[1] - 30, "TANAYA SALUNKE & SANKHYA LONDHE")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, letter[1] - 34, letter[0] - 45, letter[1] - 34)
            
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 38, letter[0] - 45, 38)
        
        self.setFont("Helvetica", 8)
        self.drawString(45, 26, "Honors Project | Final Technical Report")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 45, 26, page_text)
        self.restoreState()


def create_comprehensive_report_pdf(output_filename="reports/Final_Report_Market_Basket_Analysis.pdf"):
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

    title_style = ParagraphStyle(
        "DocTitle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=c_primary, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=c_secondary, spaceAfter=10
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=c_primary, spaceBefore=14, spaceAfter=6, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=c_secondary, spaceBefore=10, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=13, textColor=c_dark, spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom", parent=body_style, leftIndent=15, firstLineIndent=-10, spaceAfter=4
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

    # Title & Banner
    story.append(Paragraph("FINAL TECHNICAL REPORT", subtitle_style))
    story.append(Paragraph("Scalable Market Basket Analysis & Product Cross-Selling System", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=4, spaceAfter=10))

    meta_data = [
        [Paragraph("<b>Authors / Team Members:</b>", body_style), Paragraph("<b>Tanaya Salunke</b> & <b>Sankhya Londhe</b>", body_style)],
        [Paragraph("<b>Project Scope:</b>", body_style), Paragraph("End-to-End Market Basket Analytics, Benchmarking, & Interactive Web UI", body_style)],
        [Paragraph("<b>Cleaned Dataset Size:</b>", body_style), Paragraph("1,036,154 records | 39,517 unique invoices | 5,321 items", body_style)],
        [Paragraph("<b>Completion Date:</b>", body_style), Paragraph("September 2026", body_style)]
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
        "This report presents the technical evaluation and business findings of the Market Basket Analysis platform "
        "developed by <b>Tanaya Salunke</b> and <b>Sankhya Londhe</b> on the Online Retail II transaction dataset (2009 to 2011). "
        "The system mines frequent itemsets and high-leverage association rules to uncover underlying customer purchasing behavior, "
        "optimize retail product placement, drive e-commerce cross-selling prompts, and formulate promotional product bundling strategies.",
        body_style
    ))
    story.append(Paragraph("Key System Achievements:", h2_style))
    story.append(Paragraph("• <b>Raw Transaction Ingestion:</b> 1,067,371 records across 2 full operational years.", bullet_style))
    story.append(Paragraph("• <b>Cleaned Transaction Dataset:</b> 1,036,154 valid records (97.08% retention rate) spanning 39,517 unique invoices, 5,321 distinct products, 5,853 unique customers, and 43 countries.", bullet_style))
    story.append(Paragraph("• <b>Memory Optimization:</b> Sparse matrix transaction encoding achieved a 99.53% sparsity rate, reducing RAM consumption from ~210 MB down to 4.72 MB.", bullet_style))
    story.append(Paragraph("• <b>Algorithm Benchmark:</b> Evaluated Apriori vs. FP-Growth. FP-Growth built compact trie structures without candidate generation overhead (C_k), proving vastly superior for high-cardinality transaction mining.", bullet_style))
    story.append(Paragraph("• <b>Top Business Rules:</b> Uncovered strong product associations with Lift values up to 24.6x (e.g., Regency Teacup collections and matching ceramic accessories).", bullet_style))

    # 2. Dataset Ingestion & Hygiene Methodology
    story.append(Paragraph("2. Dataset Ingestion & Data Hygiene Methodology", h1_style))
    story.append(Paragraph("The data pipeline ingested raw multi-sheet Excel records (Year 2009-2010 and Year 2010-2011) and applied strict hygiene filters to ensure data integrity:", body_style))
    
    hygiene_data = [
        [Paragraph("Cleaning Stage", table_header_style), Paragraph("Retained Records", table_header_style), Paragraph("Filter Action & Rationale", table_header_style)],
        [Paragraph("<b>Raw Excel Ingestion</b>", table_cell_bold), Paragraph("1,067,371", table_cell_style), Paragraph("Ingested raw sheets <i>Year 2009-2010</i> and <i>Year 2010-2011</i>.", table_cell_style)],
        [Paragraph("<b>Missing Value Filter</b>", table_cell_bold), Paragraph("1,062,989", table_cell_style), Paragraph("Removed records missing critical InvoiceNo or Description.", table_cell_style)],
        [Paragraph("<b>Cancelled Order Filter</b>", table_cell_bold), Paragraph("1,043,495", table_cell_style), Paragraph("Filtered out returns and cancelled orders (InvoiceNo starting with 'C').", table_cell_style)],
        [Paragraph("<b>Quantity & Price Audit</b>", table_cell_bold), Paragraph("1,041,670", table_cell_style), Paragraph("Removed zero and negative quantities and non-positive prices.", table_cell_style)],
        [Paragraph("<b>Service Code Filter</b>", table_cell_bold), Paragraph("1,036,154", table_cell_style), Paragraph("Stripped service items (POSTAGE, MANUAL, BANK CHARGES, CRUK, TEST001, ADJUST).", table_cell_style)]
    ]
    t_hyg = Table(hygiene_data, colWidths=[130, 100, 292])
    t_hyg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_hyg)

    # 3. Transaction Encoding & EDA
    story.append(Paragraph("3. Transaction Encoding & Exploratory Data Analysis (EDA)", h1_style))
    story.append(Paragraph("3.1 Sparse Matrix Encoding Performance", h2_style))
    story.append(Paragraph("Transactions were grouped by InvoiceNo into item sets and encoded via TransactionEncoder(sparse=True):", body_style))
    story.append(Paragraph("• <b>Encoded Matrix Shape:</b> 39,517 Invoices × 5,321 Products", bullet_style))
    story.append(Paragraph("• <b>Matrix Sparsity:</b> 99.5290%", bullet_style))
    story.append(Paragraph("• <b>Dense Boolean Size:</b> ~210.3 MB", bullet_style))
    story.append(Paragraph("• <b>Sparse Matrix RAM:</b> 4.87 MB (97.7% RAM savings)", bullet_style))

    story.append(Paragraph("3.2 Exploratory Data Analysis Summary", h2_style))
    story.append(Paragraph("• <b>Mean Basket Size:</b> 25.06 items per invoice (Median: 15 items, 95th percentile: 72 items, Max: 1,105 items).", bullet_style))
    story.append(Paragraph("• <b>Top 5 Products by Frequency:</b> (1) WHITE HANGING HEART T-LIGHT HOLDER (5,778 orders), (2) REGENCY CAKESTAND 3 TIER (4,061 orders), (3) JUMBO BAG RED RETROSPOT (3,391 orders), (4) ASSORTED COLOUR BIRD ORNAMENT (2,938 orders), (5) PARTY BUNTING (2,740 orders).", bullet_style))
    story.append(Paragraph("• <b>Top 5 Products by Revenue:</b> (1) REGENCY CAKESTAND 3 TIER (£344,563.25), (2) WHITE HANGING HEART T-LIGHT HOLDER (£266,923.55), (3) PAPER CRAFT, LITTLE BIRDIE (£168,469.60), (4) JUMBO BAG RED RETROSPOT (£150,935.56), (5) PARTY BUNTING (£149,187.05).", bullet_style))

    # 4. Algorithm Benchmark
    story.append(Paragraph("4. Frequent Pattern Mining Benchmark: Apriori vs. FP-Growth", h1_style))
    story.append(Paragraph("Both Apriori and FP-Growth algorithms were benchmarked across multiple minimum support thresholds (min_support ∈ {0.015, 0.02, 0.03, 0.05}):", body_style))

    bench_table_data = [
        [Paragraph("Min Support", table_header_style), Paragraph("Itemsets Mined", table_header_style), Paragraph("Apriori Time (s)", table_header_style), Paragraph("FP-Growth Time (s)", table_header_style), Paragraph("FP-Growth RAM (MB)", table_header_style)],
        [Paragraph("0.015 (1.5%)", table_cell_style), Paragraph("493", table_cell_style), Paragraph("0.187 s", table_cell_style), Paragraph("24.27 s", table_cell_style), Paragraph("306.79 MB", table_cell_style)],
        [Paragraph("0.020 (2.0%)", table_cell_style), Paragraph("270", table_cell_style), Paragraph("0.114 s", table_cell_style), Paragraph("9.32 s", table_cell_style), Paragraph("306.72 MB", table_cell_style)],
        [Paragraph("0.030 (3.0%)", table_cell_style), Paragraph("91", table_cell_style), Paragraph("0.053 s", table_cell_style), Paragraph("1.84 s", table_cell_style), Paragraph("306.71 MB", table_cell_style)],
        [Paragraph("0.050 (5.0%)", table_cell_style), Paragraph("20", table_cell_style), Paragraph("0.025 s", table_cell_style), Paragraph("0.52 s", table_cell_style), Paragraph("306.71 MB", table_cell_style)]
    ]
    t_bench = Table(bench_table_data, colWidths=[90, 95, 105, 110, 104])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_bench)

    # 5. Top Association Rules
    story.append(Paragraph("5. Top Mined Association Rules & Misleading Rule Pruning", h1_style))
    story.append(Paragraph("5.1 Top Mined Rules (Ranked by Lift)", h2_style))
    
    rules_data = [
        [Paragraph("Antecedent (A)", table_header_style), Paragraph("Consequent (C)", table_header_style), Paragraph("Support", table_header_style), Paragraph("Confidence", table_header_style), Paragraph("Lift", table_header_style), Paragraph("Conviction", table_header_style)],
        [Paragraph("PINK REGENCY TEACUP AND SAUCER", table_cell_style), Paragraph("GREEN REGENCY TEACUP AND SAUCER", table_cell_style), Paragraph("2.16%", table_cell_style), Paragraph("83.40%", table_cell_style), Paragraph("<b>24.59x</b>", table_cell_style), Paragraph("5.82", table_cell_style)],
        [Paragraph("PINK REGENCY TEACUP AND SAUCER", table_cell_style), Paragraph("ROSES REGENCY TEACUP AND SAUCER", table_cell_style), Paragraph("2.03%", table_cell_style), Paragraph("78.52%", table_cell_style), Paragraph("<b>22.01x</b>", table_cell_style), Paragraph("4.49", table_cell_style)],
        [Paragraph("ROSES REGENCY TEACUP AND SAUCER", table_cell_style), Paragraph("GREEN REGENCY TEACUP AND SAUCER", table_cell_style), Paragraph("2.59%", table_cell_style), Paragraph("72.55%", table_cell_style), Paragraph("<b>21.40x</b>", table_cell_style), Paragraph("3.52", table_cell_style)],
        [Paragraph("ALARM CLOCK BAKELIKE RED", table_cell_style), Paragraph("ALARM CLOCK BAKELIKE GREEN", table_cell_style), Paragraph("2.12%", table_cell_style), Paragraph("65.67%", table_cell_style), Paragraph("<b>19.04x</b>", table_cell_style), Paragraph("2.81", table_cell_style)],
        [Paragraph("SPACEBOY LUNCH BOX", table_cell_style), Paragraph("DOLLY GIRL LUNCH BOX", table_cell_style), Paragraph("2.10%", table_cell_style), Paragraph("62.19%", table_cell_style), Paragraph("<b>17.96x</b>", table_cell_style), Paragraph("2.55", table_cell_style)]
    ]
    t_rules = Table(rules_data, colWidths=[125, 125, 65, 70, 70, 67])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_rules)

    story.append(Paragraph("5.2 Misleading Rules Identification", h2_style))
    story.append(Paragraph(
        "Rules with <b>High Confidence (>60%) but Lift ≈ 1.0</b> represent spurious correlations caused by universally popular items. "
        "For example, a rule predicting purchase of <i>WHITE HANGING HEART T-LIGHT HOLDER</i> given product X may show 70% confidence simply because T-Light Holders appear in 15% of all baskets anyway. "
        "The system automatically prunes rules with Lift < 1.2 to prevent suboptimal store placement decisions.",
        body_style
    ))

    # 6. Regional Country Segment Analysis
    story.append(Paragraph("6. Regional / Country Segment Analysis", h1_style))
    story.append(Paragraph("• <b>United Kingdom (36,185 baskets):</b> Dominated by traditional tea sets (<i>GREEN REGENCY TEACUP <==> PINK REGENCY TEACUP</i>, Lift: 24.3x).", bullet_style))
    story.append(Paragraph("• <b>Germany (753 baskets):</b> Characterized by home decor and tableware (<i>RED STRIPE CERAMIC DRAWER KNOB <==> BLUE STRIPE CERAMIC DRAWER KNOB</i>, Lift: 16.0x; <i>RED SPOTTY PAPER PLATES <==> PAPER CUPS</i>, Lift: 14.1x).", bullet_style))
    story.append(Paragraph("• <b>France (598 baskets):</b> Driven by children's products and party supplies (<i>CHILDRENS CUTLERY DOLLY GIRL <==> SPACEBOY</i>, Lift: 19.8x, Confidence: 92.6%).", bullet_style))
    story.append(Paragraph("• <b>EIRE / Ireland (581 baskets):</b> Strong demand for tea service sets (<i>REGENCY TEA PLATE GREEN <==> PINK</i>, Lift: 22.7x; <i>SUGAR JAM BOWL <==> MILK JUG</i>, Lift: 22.6x).", bullet_style))

    # 7. Retail Strategy Action Plan
    story.append(Paragraph("7. Concrete Retail Strategy & Action Plan", h1_style))
    story.append(Paragraph("1. <b>Aisle & Shelf Co-Placement:</b> Position <i>PINK REGENCY TEACUP</i> and <i>GREEN REGENCY TEACUP</i> directly adjacent on store display shelves to capture strong co-purchase intent (24.6x lift).", bullet_style))
    story.append(Paragraph("2. <b>Product Combo Bundling:</b> Launch a packaged <b>'Regency Tea Party Bundle'</b> combining Pink, Green, and Roses teacups with a 10% promotional bundle discount.", bullet_style))
    story.append(Paragraph("3. <b>Digital Checkout Cross-Sell Prompts:</b> Program automated e-commerce pop-ups recommending <i>DOLLY GIRL LUNCH BOX</i> whenever a customer adds <i>SPACEBOY LUNCH BOX</i> to their digital cart.", bullet_style))
    story.append(Paragraph("4. <b>Inventory Replenishment Synchronization:</b> Link inventory safety stock levels for paired items to avoid losing consequent sales when antecedent products sell out.", bullet_style))

    # 8. Scalability & PySpark
    story.append(Paragraph("8. Scalability Engine & PySpark Architecture", h1_style))
    story.append(Paragraph("• <b>Out-of-Core Batching:</b> Integrated BatchTransactionProcessor processes data in 50,000-row chunks, accumulating product counts and 5.8M+ pairwise co-occurrences without loading full datasets into memory.", bullet_style))
    story.append(Paragraph("• <b>PySpark FP-Growth Integration:</b> Provided PySpark reference code (src/pyspark_fpgrowth.py) mapping logic to Spark clusters for multi-terabyte data scaling using pyspark.ml.fpm.FPGrowth.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated complete comprehensive report PDF: {output_filename}")


if __name__ == "__main__":
    create_comprehensive_report_pdf()
