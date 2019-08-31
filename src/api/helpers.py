import pandas as pd
import pickle


def args_to_pandas(row_args):
    """Transform the row arguments into a pandas.DataFrame."""
    return pd.DataFrame.from_dict(row_args, orient='index').T


def _load_file_from_pickle(file):
    """Load and return a pickle file."""
    with open(file, "rb") as f:
        o_file = pickle.load(f)
    return o_file