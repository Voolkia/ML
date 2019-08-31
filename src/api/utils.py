import os
from urllib.parse import urlencode

import pandas as pd

def rows_to_urls(df, n_examples=5):
    url_samples = []
    for i in range(n_examples):
        url = urlencode(df.iloc[i].to_dict())
        html_url = f"<a href='predictions?{url}'>Example {i}</a>"
        url_samples.append(html_url)
    return url_samples


def load_sample_dataset(file_path):
    """Load example dataset."""
    return pd.read_csv(file_path, index_col=0)

