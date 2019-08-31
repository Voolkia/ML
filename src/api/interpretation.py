import numpy as np
from treeinterpreter import treeinterpreter as ti


def get_feature_contributions(model, row):
    """Return a dictionary of the contribution by feature."""
    prediction, bias, contributions = ti.predict(model, row)
    impact = np.around(calc_prop_impact(contributions[0][:, 0]),5)
    return contributions_to_json(row.columns, impact)

def calc_prop_impact(contributions):
    sum_abs = np.abs(contributions).sum()
    prop_imp = (contributions / sum_abs)
    return prop_imp

def contributions_to_json(columns, contributions):
    """Generate the contributions json.
    
    Parameters
    ----------
    columns: pandas.core.indexes.base.Index
    
    contributions: numpy.ndarray
    
    TODO:
        - finish docstring
    """
    json = {}
    idxs = np.argsort(contributions)
    for i in idxs:
        json[columns[i]] = contributions[i]
    return json
