"""
Transaction Encoding Module for Market Basket Analysis.
Converts cleaned transaction records into memory-efficient basket representations
(list-of-lists and SciPy sparse boolean matrices).
"""

import os
import logging
import pandas as pd
import numpy as np
from scipy import sparse
from mlxtend.preprocessing import TransactionEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_cleaned_data(filepath="data/processed/cleaned_transactions.parquet"):
    """Load cleaned dataset from Parquet (or CSV if Parquet unavailable)."""
    if os.path.exists(filepath):
        logging.info(f"Loading cleaned transactions from: {filepath}")
        return pd.read_parquet(filepath)
    csv_path = filepath.replace(".parquet", ".csv")
    if os.path.exists(csv_path):
        logging.info(f"Loading cleaned transactions from CSV fallback: {csv_path}")
        return pd.read_csv(csv_path)
    raise FileNotFoundError(f"Cleaned dataset not found at {filepath}")


def create_basket_lists(df):
    """
    Group transactions by InvoiceNo into a list of item sets/lists.
    Returns:
        baskets: list of lists of item descriptions
        invoice_ids: list of corresponding InvoiceNo identifiers
    """
    logging.info("Grouping transactions into basket lists by InvoiceNo...")
    grouped = df.groupby("InvoiceNo")["Description"].apply(lambda items: sorted(list(set(items))))
    baskets = grouped.tolist()
    invoice_ids = grouped.index.tolist()
    logging.info(f"Created {len(baskets):,} basket lists.")
    return baskets, invoice_ids


def encode_transactions_sparse(baskets):
    """
    Convert list of transaction baskets into a SciPy sparse boolean matrix & pandas SparseDataFrame.
    Memory efficient for large datasets with high cardinality.
    """
    logging.info("Encoding transaction baskets using sparse TransactionEncoder...")
    te = TransactionEncoder()
    te_ary_sparse = te.fit(baskets).transform(baskets, sparse=True)
    
    # te_ary_sparse is a scipy.sparse.csr_matrix
    columns = te.columns_
    logging.info(f"Encoded matrix shape: {te_ary_sparse.shape} (Baskets x Items). "
                 f"Sparsity: {1.0 - (te_ary_sparse.nnz / (te_ary_sparse.shape[0] * te_ary_sparse.shape[1])):.4%}")
    
    # Wrap in pandas sparse DataFrame
    sparse_df = pd.DataFrame.sparse.from_spmatrix(te_ary_sparse, columns=columns)
    return sparse_df, te_ary_sparse, columns


def get_memory_usage_mb(df_or_matrix):
    """Calculate approximate memory usage of DataFrame or SciPy matrix in MB."""
    if isinstance(df_or_matrix, pd.DataFrame):
        return df_or_matrix.memory_usage(deep=True).sum() / (1024 * 1024)
    elif sparse.issparse(df_or_matrix):
        # data + indices + indptr bytes
        nbytes = df_or_matrix.data.nbytes + df_or_matrix.indices.nbytes + df_or_matrix.indptr.nbytes
        return nbytes / (1024 * 1024)
    elif isinstance(df_or_matrix, np.ndarray):
        return df_or_matrix.nbytes / (1024 * 1024)
    return 0.0


if __name__ == "__main__":
    df = load_cleaned_data()
    baskets, invoice_ids = create_basket_lists(df)
    sparse_df, sparse_matrix, items = encode_transactions_sparse(baskets)
    mem_sparse = get_memory_usage_mb(sparse_df)
    mem_matrix = get_memory_usage_mb(sparse_matrix)
    print(f"\n--- Encoding Summary ---")
    print(f"Total Transactions (Baskets): {len(baskets):,}")
    print(f"Total Unique Products: {len(items):,}")
    print(f"Sparse Matrix Memory: {mem_matrix:.2f} MB")
    print(f"Sparse DataFrame Memory: {mem_sparse:.2f} MB")
