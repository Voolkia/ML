"""
CONFIGURACIÓN PARA LA ETAPA DE CARGA DE DATOS

En este script se guardan las variables correspondientes a los nombres
de los archivos así como también las columnas que se usan en cada uno.

NOTE: Se deben modificar solamente aquellas variables que comiencen con el
      prefijo ARCHIVO_ o SEP_
"""

# MODIFICAR ESTA PARTE
ARCHIVO_POLIZAS = "tables/VIGABT_POLIZAS.tsv"
ARCHIVO_PAGOS = "tables/PAGOS.tsv"
ARCHIVO_CLIENTES = "tables/TB_CIF.tsv"
ARCHIVO_SINIESTROS = "tables/DSS_SINIESTROS_AUTOS.csv"
ARCHIVO_INTERACCIONES = "tables/TB_INTERACCIONES_2.tsv"

SEP_POLIZAS = "\t"
SEP_PAGOS = "\t"
SEP_CLIENTES = "\t"
SEP_SINIESTROS = ";"
SEP_INTERACCIONES = "\t"

PATH_DATASET = "DATASET_FINAL.feather"
PATH_MODELO = "model.md"
PATH_PREDICCIONES = "PREDICCIONES.csv"

"""
Modificar estos valores de acuerdo al período analizado.
NOTE: Formato: aaaa/mm/dd
"""
PERIODO_INI = '2019-01-01'
PERIODO_FIN = '2019-06-30'

# NO MODIFICAR ESTO
COLS_POLIZA = [
    'CIF_ID',
    'MCA_VIGENCIA',
    'NUM_SECU_POL',
    'COD_INICIADOR',
    'FECHA_VIG_POL',
]
COLS_PAGOS = [
    'COD_COBRO',
    'COD_SITUACION',
    'FECHA_VTO',
    'FEC_PAGO',
    'MONTO_PAGO',
    'NUM_SECU_POL'
]
COLS_CLIENTES = [
    'ANO_DE_NACIMIENTO',
    'ID',
    'POSICION_IVA'
]
COLS_SINIESTROS = [
    "NUM_SECU_POL",
    "MODELO_VEHICULO",
    "FEC_DENU_SINI",
    "FECHA_LIQUIDACION",
    "FECHA_RECHAZO"
]
COLS_INTERACCIONES = [
    'ID',
    'CIF_ID',
    'FECHA',
    'IN_OUT'
]
