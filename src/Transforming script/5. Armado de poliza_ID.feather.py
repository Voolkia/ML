
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


table = "TB_POLIZAS_1a.tsv"
location = "../../data/raw"
sep = '\t'
encoding = 'latin1'
decimal = ','


# In[3]:


df_polizas = pd.read_csv(f"{location}/{table}",
                         sep=sep,
                         encoding=encoding,
                         decimal=decimal,
                         usecols = ["NUM_SECU_POL", "CIF_ID"])


# In[4]:


df_polizas.head()


# In[5]:


df_polizas.drop_duplicates(inplace=True)


# In[6]:


df_polizas.reset_index(drop=True).to_feather("poliza_x_cliente.feather")


# In[7]:


df_polizas.shape


# In[8]:


df_polizas['CIF_ID'].nunique()

