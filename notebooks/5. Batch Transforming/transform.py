from functools import reduce
from config import PERIODO_INI, PERIODO_FIN
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None


def check_periods(col):
    print(pd.DataFrame(
            {"Rango": [col.min(), col.max()]},
            index=['MIN', 'MAX'])
          )


# HELPER FUNCTIONS
def transform_date(s):
    dates = {date: pd.to_datetime(date) for date in s.unique()}
    return s.map(dates)


def dates_to_int(dates):
    periodos = {fecha: i + 1
                for i, fecha
                in enumerate(sorted(dates.unique(),
                                    reverse=True))
                }
    return dates.map(periodos)


def simplify_history(x):
    return "".join(["1" if int(n) > 0 else "0" for n in x.split(" ")])


def to_yearmonth(s):
    dates = {date: pd.Timestamp(date).strftime('%Y-%m') for date in s.unique()}
    return s.map(dates)


# TRANSFORMING PIPELINE FUNCTIONS
def transform_polizas(df_polizas):
    df_polizas['FECHA_VIG_POL'] = transform_date(df_polizas['FECHA_VIG_POL'])
    df_polizas['mes_anio_vig'] = df_polizas['FECHA_VIG_POL'].dt.strftime('%Y-%m')
    to_pivot = df_polizas[["CIF_ID",
                           "NUM_SECU_POL",
                           "MCA_VIGENCIA",
                           "mes_anio_vig"]].drop_duplicates()
    del df_polizas
    df_polizas_pivoted = to_pivot.pivot_table(index='CIF_ID',
                                              columns=['mes_anio_vig'],
                                              values=['MCA_VIGENCIA'],
                                              aggfunc='count',
                                              fill_value=0)
    del to_pivot
    df_polizas_pivoted = df_polizas_pivoted.astype(str)
    df_polizas_pivoted["history"] = df_polizas_pivoted.apply(" ".join, axis=1)
    new_df = pd.DataFrame(df_polizas_pivoted.index)
    new_df = new_df.set_index('CIF_ID')
    new_df["hist_polizas"] = df_polizas_pivoted["history"]
    del df_polizas_pivoted
    return new_df


def add_id(df, with_table, id_col, fk_col):
    df_aux = pd.read_csv(with_table,
                         sep='\t',
                         encoding='latin1',
                         decimal=',',
                         usecols=[id_col, fk_col]) 
    return pd.merge(df, df_aux, on=fk_col, how='inner')


def transform_pagos(df_pagos):
    df_pagos["FECHA_VTO"] = transform_date(df_pagos["FECHA_VTO"])
    df_pagos["FEC_PAGO"] = transform_date(df_pagos["FEC_PAGO"])
    df_pagos["demora_pago"] = ((df_pagos["FEC_PAGO"] - df_pagos["FECHA_VTO"]) / np.timedelta64(1, 'M')).astype("float")
    df_pagos.loc[df_pagos["COD_COBRO"] == "TM", "COD_COBRO"] = "TA"
    # FILTER CURRENT PERIOD
    df_pagos = df_pagos[df_pagos["FECHA_VTO"].between(PERIODO_INI,
                                                      PERIODO_FIN)]
    # TRANSFORM DATE TO PERIOD
    df_pagos["FECHA_VTO"] = to_yearmonth(df_pagos["FECHA_VTO"].dropna())
    df_pagos["periodo"] = dates_to_int(df_pagos["FECHA_VTO"])
    # BEGIN PIVOTING
    to_pivot = df_pagos[["CIF_ID","demora_pago","periodo","COD_COBRO","COD_SITUACION","MONTO_PAGO"]]
    df_pagos_datediff = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo"], values=["demora_pago","MONTO_PAGO"], aggfunc="mean")
    df_pagos_datediff = pd.DataFrame(df_pagos_datediff.to_records())
    df_pagos_datediff = df_pagos_datediff.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_").replace("'",""))
    df_cods = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo","COD_SITUACION"], aggfunc="size")
    df_cods = pd.DataFrame(df_cods.to_records())
    df_cods = df_cods.rename(columns=lambda x: x.replace("(","").replace(")", "").replace(", ","_SITUACION_").replace("'", ""))
    df_codc = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo","COD_COBRO"], aggfunc="size")
    df_codc = pd.DataFrame(df_codc.to_records())
    df_codc = df_codc.rename(columns=lambda x: x.replace("(","").replace(")", "").replace(", ","_COBRO_").replace("'", ""))
    del to_pivot
    del df_pagos
    return reduce(lambda left, right: pd.merge(left, right, on=['CIF_ID'], how='outer'), [df_cods, df_codc, df_pagos_datediff])


def transform_siniestros(df_sini):
    df_sini.drop_duplicates(subset=["NUM_SECU_POL", "FEC_DENU_SINI"],
                            keep='last',
                            inplace=True)
    df_sini["FEC_DENU_SINI"] = transform_date(df_sini["FEC_DENU_SINI"])
    df_sini["FECHA_LIQUIDACION"] = transform_date(df_sini["FECHA_LIQUIDACION"])
    df_sini["FECHA_RECHAZO"] = transform_date(df_sini["FECHA_RECHAZO"])
    # FILTER CURRENT PERIOD
    df_sini = df_sini[df_sini["FEC_DENU_SINI"].between(PERIODO_INI,
                                                       PERIODO_FIN)]
    check_periods(df_sini["FEC_DENU_SINI"])
    # TRANSFORM DATE TO PERIOD
    df_sini["FEC_DENU_SINI"] = to_yearmonth(df_sini["FEC_DENU_SINI"].dropna())
    df_sini["FECHA_LIQUIDACION"] = to_yearmonth(df_sini["FECHA_LIQUIDACION"].dropna())
    df_sini["FECHA_RECHAZO"] = to_yearmonth(df_sini["FECHA_RECHAZO"].dropna())
    periodos = {fecha: i + 1
                for i, fecha in enumerate(sorted(df_sini["FEC_DENU_SINI"].unique(),
                                                 reverse=True))
                }
    df_sini["periodo_denu_sini"] = df_sini["FEC_DENU_SINI"].map(periodos)
    df_sini["periodo_liquidacion_sini"] = df_sini["FECHA_LIQUIDACION"].map(periodos)
    df_sini["periodo_rechazo_sini"] = df_sini["FECHA_RECHAZO"].map(periodos)
    # BEGIN PIVOTING
    to_pivot = df_sini[["CIF_ID",
                        "NUM_SECU_POL",
                        "periodo_denu_sini",
                        "periodo_liquidacion_sini",
                        "periodo_rechazo_sini"]]
    df_sini = to_pivot.pivot_table(index='CIF_ID',
                                   columns=['periodo_denu_sini'],
                                   values=['NUM_SECU_POL',
                                           'periodo_liquidacion_sini',
                                           'periodo_rechazo_sini'],
                                   aggfunc='count',
                                   fill_value=0)
    df_sini = pd.DataFrame(df_sini.to_records())
    df_sini = df_sini.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_").replace("'","").replace("NUM_SECU_POL","periodo_sini"))
    return df_sini


def transform_interacciones(df):
    df = df[~pd.to_numeric(df['ID'], errors='coerce').isnull()]
    # SOME CLEANING
    to_check = []
    for val in df["CIF_ID"].unique():
        try:
            float(val)
        except Exception:
            to_check.append(val)
    df = df[~df["CIF_ID"].isin(to_check)]
    to_check = []
    for val in df["ID"].unique():
        try:
            int(val)
        except Exception:
            to_check.append(val)
    df = df[~df["ID"].isin(to_check)]
    df = df.drop(columns='ID').astype({'CIF_ID': 'float64'})
    df = df[df["IN_OUT"].isin(['O', 'I', 'A'])]
    df["FECHA"] = df["FECHA"].str.slice(stop=10)
    df.loc[df["FECHA"].str.contains(" [0-9]", na=False), "FECHA"] = df.loc[df["FECHA"].str.contains(" [0-9]", na=False), "FECHA"].str.slice(stop=8) 
    df["FECHA"] = df["FECHA"].str.replace(" ", "")
    df["periodo"] = transform_date(df["FECHA"])
    # FILTER CURRENT PERIOD
    df = df[df["periodo"].between(PERIODO_INI, PERIODO_FIN)]
    check_periods(df["periodo"])
    df = df[["CIF_ID", "IN_OUT", "periodo"]]
    # TRANSFORM DATE TO PERIOD
    df["periodo"] = to_yearmonth(df["periodo"].dropna())
    df["periodo_int"] = dates_to_int(df["periodo"])
    # BEGIN PIVOTING
    to_pivot = df[["CIF_ID", "IN_OUT", "periodo_int"]]
    df = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo_int", "IN_OUT"], aggfunc="size")
    df = pd.DataFrame(df.to_records())
    df = df.rename(columns=lambda x: x.replace("(", "").replace(")", "").replace(", ", "_TIPOINT_").replace("'", "")) 
    return df
