import os
from helpers import _load_file_from_pickle
from configs import FILE_MAPPER
import numpy as np

def load_model(model_file):
    """Load the dump model."""
    return _load_file_from_pickle(model_file)


def load_columns(columns_file):
    """Load the array of columns use in the dump model."""
    return _load_file_from_pickle(columns_file)


def load_mapper(mapper_file):
    """Load and return the categorical feature mapper."""
    return _load_file_from_pickle(mapper_file)


def feature_transformation(dataset, inplace=False):
    """Map the real value with the transformed value."""
    if inplace:
        df = dataset
    else:
        df = dataset.copy()
    # specific feature format
    df = features_formatter(df)
    df = str_to_bool(df)
    df = str_to_none(df)
    # replace Nulls by np.nan
    # df.fillna(-1, inplace=True)
    # categorical to num transformation
    mapper = load_mapper(FILE_MAPPER)
    cat_cols = list(set(mapper.keys()).intersection(df.columns))
    # df = df.astype(float)
    for col in cat_cols:
        unique_values = df.loc[:, col].unique()
        keys = mapper[col].keys()
        new_vals = list(set(unique_values) - keys)
        if(new_vals):
            # replace new values by np.nan
            df.loc[:,col].replace(new_vals, -1, inplace=True)
        else:
            df.loc[:,col] = df.loc[:,col].replace(mapper[col])
    df.fillna(-1, inplace=True)
    return df


def features_formatter(dataset, inplace=False):
    """Make specific features transformations."""
    if inplace:
        df = dataset
    else:
        df = dataset.copy()
    # normalizing TIPO_EXPED 
    if "TIPO_EXPED" in df.columns:
        df["TIPO_EXPED"] = df["TIPO_EXPED"].astype("str").str.zfill(3)
    return df


def str_to_bool(dataset, inplace=False):
    """Replace String False and True by 0 and 1."""
    if inplace:
        df = dataset
    else:
        df = dataset.copy()
    df.replace("True", 1, inplace=True)
    df.replace("False", 0, inplace=True)
    return df


def str_to_none(dataset, inplace=False):
    """Replace string with Null type string to np.nan."""
    if inplace:
        df = dataset
    else:
        df = dataset.copy()
    non_types = ["None", "nan", "np.nan", "NaN"]
    df.replace(non_types, np.nan, inplace=True)
    return df


def feature_inverse_mapper():
    """Map the transformed value with the real value."""
    pass
