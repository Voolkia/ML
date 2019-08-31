
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# In[2]:


table = "TB_PAGOS_1a.tsv"
location = "../../data/raw"
sep = '\t'
encoding = 'latin1'
decimal = ','


# In[3]:


usable_cols = ['COD_COBRO',
    'COD_SITUACION',
    'FECHA_VTO',
    'FEC_PAGO',
    'MONTO_PAGO',
    'NUM_SECU_POL']


# In[4]:


chunks = pd.read_csv(f"{location}/{table}",
                     sep=sep,
                     encoding=encoding,
                     decimal=decimal,
                     chunksize=1000000,
                     iterator=True,
                     usecols = usable_cols)
df = pd.concat(chunks)


# In[5]:


df.to_feather("pagos.feather")

