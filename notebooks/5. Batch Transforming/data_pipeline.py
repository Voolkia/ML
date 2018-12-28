from config import ARCHIVO_POLIZAS, COLS_POLIZA, SEP_POLIZAS,\
                   ARCHIVO_PAGOS, COLS_PAGOS, SEP_PAGOS,\
                   ARCHIVO_CLIENTES, COLS_CLIENTES, SEP_CLIENTES,\
                   ARCHIVO_SINIESTROS, COLS_SINIESTROS, SEP_SINIESTROS,\
                   ARCHIVO_INTERACCIONES, COLS_INTERACCIONES,\
                   SEP_INTERACCIONES, PATH_DATASET
from transform import transform_polizas, add_id,\
                      transform_pagos, transform_siniestros,\
                      transform_interacciones
from functools import reduce
import pandas as pd
import numpy as np
import re


if __name__ == "__main__":

    # TRANSFORM POLIZAS
    print("---POLIZAS---")
    df_polizas = pd.read_csv(ARCHIVO_POLIZAS,
                             sep=SEP_POLIZAS,
                             encoding='latin1',
                             decimal=',',
                             usecols=COLS_POLIZA)
    df_polizas = transform_polizas(df_polizas)

    # TRANSFORM PAGOS
    print("---PAGOS---")
    df_pagos = pd.read_csv(ARCHIVO_PAGOS,
                           sep=SEP_PAGOS,
                           encoding='latin1',
                           decimal=',',
                           usecols=COLS_PAGOS)
    df_pagos = add_id(df_pagos, ARCHIVO_POLIZAS, 'CIF_ID', 'NUM_SECU_POL')
    df_pagos = transform_pagos(df_pagos)

    # TRANSFORM SINIESTROS
    print("---SINIESTROS---")
    df_sini = pd.read_csv(ARCHIVO_SINIESTROS,
                          sep=SEP_SINIESTROS,
                          encoding='latin1',
                          decimal=',',
                          usecols=COLS_SINIESTROS)
    df_sini = add_id(df_sini, ARCHIVO_POLIZAS, 'CIF_ID', 'NUM_SECU_POL')
    df_sini = transform_siniestros(df_sini)

    # TRANSFORM INTERACCIONES
    print("---INTERACCIONES---")
    df_interacciones = pd.read_csv(ARCHIVO_INTERACCIONES,
                                   sep=SEP_INTERACCIONES,
                                   encoding='latin1',
                                   decimal=',',
                                   usecols=COLS_INTERACCIONES)
    df_interacciones = transform_interacciones(df_interacciones)

    # LOAD CLIENTES
    print("---CLIENTES---")
    df_clientes = pd.read_csv(ARCHIVO_CLIENTES,
                              sep=SEP_CLIENTES,
                              encoding='latin1',
                              decimal=',',
                              usecols=COLS_CLIENTES)
    df_clientes = df_clientes.rename(columns={"ID": "CIF_ID"})

    # MERGE EVERYTING
    print("---MERGING---")
    df_polizas_int = pd.merge(df_polizas,
                              df_interacciones,
                              on=['CIF_ID'],
                              how='left')
    df_bajas_int_sini = pd.merge(df_polizas_int,
                                 df_sini,
                                 on=['CIF_ID'],
                                 how='left')
    df_bajas_int_sini = df_bajas_int_sini.fillna(0)
    df_merged = reduce(lambda left, right: pd.merge(left,
                                                    right,
                                                    on=['CIF_ID'],
                                                    how='inner'),
                       [df_bajas_int_sini, df_pagos, df_clientes]
                       )
    print(df_merged.shape)

    # ADD MISSING FEATURES
    to_check = ['_COBRO_BA',
                '_COBRO_CC',
                '_COBRO_PP',
                '_COBRO_SJ',
                '_COBRO_TA',
                '_SITUACION_AM',
                '_SITUACION_CT',
                '_SITUACION_EP',
                '_SITUACION_PP',
                '_TIPOINT_A',
                '_TIPOINT_I',
                '_TIPOINT_O']
    for i in range(1, 7):
        for col in to_check:
            if(f'{i}{col}' not in df_merged.columns):
                print(f'adding {i}{col}')
                df_merged[f'{i}{col}'] = np.nan

    # ADJUST COLUMN NAMES TO MATCH TRAINING COLUMNS
    # TODO: CHANGE FOR RENAME
    periodic_cols = set([''.join([s for s in col if not s.isdigit()]) for col in df_merged[[col for col in df_merged.columns if re.search(f'\d', col)]].columns])
    for pcol in periodic_cols:
        regex_range = "|".join([str(i) for i in range(1, 7)])
        regex = f'{pcol}({regex_range})$|^({regex_range}){pcol}'
        columns = [col for col in df_merged.columns if re.search(regex, col)]
        df_merged[[f"{i}_{pcol}" for i in range(1, 7)]] = df_merged[columns]
        df_merged = df_merged.drop(columns, axis=1)        


    # ADD CALCULATED ATTRIBUTES
    # POLIZAS PER PERIOD
    df_merged[[f"polizas_{i}"
               for i in range(6, 0, -1)]] = df_merged["hist_polizas"].str.split(" ", expand=True).iloc[:,0:6].astype(float)

    # DIFFERENCES BETWEEN PERIODS
    for i in range(5, 0, -1):
        df_merged[f"diff_cant_polizas_{i}"] = df_merged[f"polizas_{i}"] - df_merged[f"polizas_{i+1}"]    
        current_int = [col for col in df_merged.columns if re.search(f'({i})__TIPOINT', col)]
        next_int = [col for col in df_merged.columns if re.search(f'({i+1})__TIPOINT', col)]
        df_merged[f"diff_cant_int_{i}"] =  df_merged[current_int].sum(axis=1) - df_merged[next_int].sum(axis=1)

    df_merged = df_merged.drop(["hist_polizas"], axis=1)
    print(df_merged.shape)

    # WRITE DATASET INTO ANOTHER FILE
    # FEATHER FORMAT
    df_merged.to_feather(PATH_DATASET)
