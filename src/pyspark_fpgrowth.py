"""
PySpark Distributed FP-Growth Architecture Module.
Demonstrates how Market Basket Analysis scales to multi-terabyte datasets using
Apache Spark MLlib (pyspark.ml.fpm.FPGrowth).
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


PYSPARK_FPGROWTH_CODE_SNIPPET = """
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.fpm import FPGrowth

# 1. Initialize PySpark Session
spark = SparkSession.builder \\
    .appName("ScalableMarketBasketAnalysis") \\
    .config("spark.driver.memory", "8g") \\
    .config("spark.executor.memory", "8g") \\
    .getOrCreate()

# 2. Ingest cleaned transaction Parquet/CSV file
df = spark.read.parquet("data/processed/cleaned_transactions.parquet")

# 3. Group by InvoiceNo into array of distinct products
baskets_df = df.groupBy("InvoiceNo") \\
    .agg(F.collect_set("Description").alias("items"))

# 4. Instantiate PySpark FP-Growth Model
fp_growth = FPGrowth(
    itemsCol="items",
    minSupport=0.02,
    minConfidence=0.3
)

# 5. Fit Distributed Model on Spark Cluster
model = fp_growth.fit(baskets_df)

# 6. Extract Frequent Itemsets & Association Rules
frequent_itemsets = model.freqItemsets
association_rules = model.associationRules

# Display Top Association Rules by Lift/Confidence
association_rules.sort(F.col("lift").desc()).show(20, truncate=False)
"""


def explain_pyspark_architecture():
    """Output explanation and PySpark architecture workflow."""
    logging.info("Generating PySpark FP-Growth Architecture Mapping...")
    explanation = (
        "========================================================================\n"
        "         PYSPARK DISTRIBUTED FP-GROWTH SCALABILITY ARCHITECTURE         \n"
        "========================================================================\n\n"
        "For enterprise retail datasets (100M+ transactions), single-node memory\n"
        "and Python dataframes reach system limits. PySpark's FP-Growth divides\n"
        "the FP-Tree construction across a cluster of worker nodes using Spark RDDs.\n\n"
        "Key Advantages of PySpark FP-Growth:\n"
        "1. Distributed FP-Tree Construction: Partition-based item counting & conditional tree building.\n"
        "2. Out-of-Core Execution: Handles datasets larger than total cluster RAM using disk spill.\n"
        "3. Integration with Spark SQL & Data Lake: Queries Parquet/Delta Lake files directly.\n\n"
        "PySpark Reference Code:\n"
        "------------------------------------------------------------------------\n"
        f"{PYSPARK_FPGROWTH_CODE_SNIPPET}\n"
        "------------------------------------------------------------------------\n"
    )
    return explanation


if __name__ == "__main__":
    print(explain_pyspark_architecture())
