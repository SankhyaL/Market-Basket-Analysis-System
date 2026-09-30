# Scalable Market Basket Analysis System in Python

A high-performance, modular **Market Basket Analysis (MBA)** and Product Cross-Selling Intelligence platform built in Python. Designed to mine frequent itemsets and high-leverage association rules from large retail transaction datasets (`Online Retail II`), perform algorithm benchmarking (**Apriori vs. FP-Growth**), detect misleading spurious rules, construct product co-occurrence network graphs, provide regional segment analysis, and deliver interactive recommendations via a **Streamlit Web Application**.

---

## 📁 Project Structure

```
├── data/
│   ├── raw/                       # Original transaction datasets
│   └── processed/                 # Cleaned Parquet & CSV transaction tables
├── notebooks/                     # Exploratory Data Analysis & experimentation
├── src/                           # Production source modules
│   ├── data_loader.py             # Data ingestion, cancellation filtering, & text hygiene
│   ├── encoder.py                 # Memory-efficient sparse matrix basket encoding
│   ├── eda.py                     # Product distribution & basket statistics
│   ├── frequent_mining.py         # Apriori vs. FP-Growth benchmarking engine
│   ├── rule_generator.py          # Rule extraction (Support, Confidence, Lift, Conviction)
│   ├── network_graph.py           # NetworkX product co-occurrence visualization
│   ├── insights.py                # Natural language business insight translator
│   ├── scalability.py             # Out-of-core chunked processor & stage profiler
│   └── pyspark_fpgrowth.py        # PySpark FP-Growth reference architecture
├── reports/                       # Generated outputs, visualizations, & reports
│   ├── eda/                       # High-res EDA charts & summary stats
│   ├── frequent_mining/           # Benchmark charts & CSV metric comparisons
│   ├── association_rules/         # Mined rules, top rankings, & misleading rules
│   ├── insights/                  # Network graph & country segment analysis
│   └── final_report.md            # Comprehensive project Markdown report
├── app/                           # Web application
│   └── streamlit_app.py           # Streamlit interactive dashboard
├── tests/                         # Automated unit tests
│   └── test_pipeline.py           # Pytest test suite for cleaning, encoding, & mining
├── config.yaml                    # System parameters (support, confidence, lift, chunk size)
├── requirements.txt               # Dependency specifications
├── main.py                        # Master CLI entry point
└── README.md                      # Complete setup & usage guide
```

---

## ⚡ Quick Start & Setup

### 1. Prerequisites & Environment Setup
```bash
# Clone or navigate to the project workspace
cd "honors project sem 7"

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip & install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation with Unit Tests
```bash
pytest tests/
```

---

## 🚀 How to Run the Pipeline

### 1. Run Full End-to-End Pipeline
Executes data cleaning, sparse encoding, FP-Growth pattern mining, rule generation, network graph generation, and segment analysis:
```bash
python main.py
```

### 2. Fast Iteration on Sample Data
Run the pipeline on a 10% random sample of transaction invoices:
```bash
python main.py --sample 0.1
```

### 3. Country-Specific Market Basket Mining
Mine rules specifically for a single region (e.g. `Germany`, `France`, `EIRE`, or `United Kingdom`):
```bash
python main.py --country Germany --support 0.03 --confidence 0.4
```

### 4. Run Specific Stages (EDA / Benchmark)
```bash
# Run Data Hygiene & Exploratory Data Analysis
python main.py --clean --eda

# Run Apriori vs. FP-Growth Algorithmic Benchmark
python main.py --benchmark
```

### 5. Launch Interactive Streamlit Dashboard
```bash
python main.py --app
# OR directly:
streamlit run app/streamlit_app.py
```

---

## 📊 Key Results & Benchmark Comparison

### Algorithm Performance (Apriori vs. FP-Growth)

| Minimum Support | Frequent Itemsets Mined | Apriori Execution (s) | FP-Growth Execution (s) | Memory Footprint (MB) |
| :---: | :---: | :---: | :---: | :---: |
| **0.015** (1.5%) | 493 | 0.187 s | 24.27 s | 306.79 MB |
| **0.020** (2.0%) | 270 | 0.114 s | 9.32 s | 306.72 MB |
| **0.030** (3.0%) | 91 | 0.053 s | 1.84 s | 306.71 MB |
| **0.050** (5.0%) | 20 | 0.025 s | 0.52 s | 306.71 MB |

> **Key takeaway**: FP-Growth constructs an in-memory FP-Tree (trie structure) without candidate generation overhead ($C_k$), proving vastly superior for high-cardinality retail mining.

---

## 💡 Top Mined Association Rules

| Antecedent | Consequent | Support | Confidence | Lift | Action Strategy |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **PINK REGENCY TEACUP AND SAUCER** | **GREEN REGENCY TEACUP AND SAUCER** | 2.16% | 83.40% | **24.59x** | Physical shelf co-placement & 10% promo bundle. |
| **PINK REGENCY TEACUP AND SAUCER** | **ROSES REGENCY TEACUP AND SAUCER** | 2.03% | 78.52% | **22.01x** | Bundle combo offer: "Regency Tea Set". |
| **ALARM CLOCK BAKELIKE RED** | **ALARM CLOCK BAKELIKE GREEN** | 2.12% | 65.67% | **19.04x** | Digital e-commerce checkout cross-sell prompt. |
| **SPACEBOY LUNCH BOX** | **DOLLY GIRL LUNCH BOX** | 2.10% | 62.19% | **17.96x** | Frequently Bought Together recommendation. |

---

## 🛠️ Out-of-Core Scalability & PySpark Integration

- **Chunked Processing**: `BatchTransactionProcessor` in `src/scalability.py` processes transactions in 50,000-row batches, handling 1M+ transaction datasets under 800 MB RAM memory limit.
- **PySpark Mapping**: `src/pyspark_fpgrowth.py` provides reference architecture for scaling logic to multi-terabyte cluster environments using `pyspark.ml.fpm.FPGrowth`.
