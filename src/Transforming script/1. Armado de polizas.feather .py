
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# In[2]:


table = "TB_POLIZAS_1a.tsv"
location = "../../data/raw"
sep = '\t'
encoding = 'latin1'
decimal = ','


# In[3]:


cols_poliza = [
    'CIF_ID',
    'MCA_VIGENCIA',
    'NUM_SECU_POL',
    'COD_INICIADOR',
    'FECHA_VIG_POL',
 ]


# ## Creating poilizas.feahter

# In[4]:


chunks = pd.read_csv(f"{location}/{table}",
                     sep=sep,
                     encoding=encoding,
                     decimal=decimal,
                     chunksize=1000000,
                     iterator=True,
                     usecols = cols_poliza)
df = pd.concat(chunks)


# In[5]:


df.shape 


# In[6]:


df['CIF_ID'].nunique()


# In[7]:


df.to_feather("../../data/interim/polizas.feather")

