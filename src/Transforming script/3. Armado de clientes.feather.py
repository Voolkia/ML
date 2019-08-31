
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# In[2]:


table = "TB_CIF.tsv"
location = "../../data/raw"
sep = '\t'
encoding = 'latin1'
decimal = ','


# In[3]:


usable_cols = [
 'ANO_DE_NACIMIENTO',
 'ID',
 'POSICION_IVA']


# ## Creating clientes.feahter

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


df.to_feather("../../data/interim/clientes.feather")

