
# coding: utf-8

# In[10]:


import pandas as pd


# In[11]:


df_sini = pd.read_feather("siniestros.feather")


# In[12]:


df_ids = pd.read_feather("poliza_x_cliente.feather")


# Verificación de cruce

# In[13]:


len(set(df_ids["NUM_SECU_POL"]).intersection(set(df_sini["NUM_SECU_POL"]))) / len(df_ids)


# In[14]:


len(set(df_sini["NUM_SECU_POL"]).intersection(set(df_ids["NUM_SECU_POL"]))) / len(df_sini)


# ### Agregamos CIF_ID a los Siniestros

# In[15]:


df_sini_id = pd.merge(df_sini, df_ids, on=['NUM_SECU_POL'], how='left')


# In[16]:


df_sini_id.drop_duplicates(subset=["NUM_SECU_POL", "FEC_DENU_SINI"], keep='last', inplace=True)


# ### Agrupamos siniestros por periodo

# In[17]:


data = {fecha:i + 1 for i,fecha in enumerate(sorted(df_sini_id["FEC_DENU_SINI"].unique()))}


# In[18]:


data


# In[19]:


df_sini_id["periodo_denu_sini"] = df_sini_id["FEC_DENU_SINI"].map(data)


# In[20]:


df_sini_id["periodo_liquidacion_sini"] = df_sini_id["FECHA_LIQUIDACION"].map(data)


# In[21]:


df_sini_id["periodo_rechazo_sini"] = df_sini_id["FECHA_RECHAZO"].map(data)


# In[22]:


to_pivot = df_sini_id[["CIF_ID","NUM_SECU_POL","periodo_denu_sini","periodo_liquidacion_sini","periodo_rechazo_sini"]]


# ### Pivots por CIF_ID

# In[23]:


pd.set_option("display.max_columns", 500)


# In[24]:


df_sini = to_pivot.pivot_table(index='CIF_ID',columns=['periodo_denu_sini'], values=['NUM_SECU_POL','periodo_liquidacion_sini','periodo_rechazo_sini'],aggfunc='count', fill_value=0)


# In[25]:


df_sini.head()


# Reagrupamos los DF

# In[26]:


df_sini = pd.DataFrame(df_sini.to_records())


# In[27]:


df_sini.head()


# ** Cambio de nombre de columnas **

# In[28]:


df_sini.columns


# In[29]:


df_sini = df_sini.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_").replace("'","").replace("NUM_SECU_POL","periodo_sini"))


# In[30]:


df_sini.columns


# In[31]:


len(df_sini.columns)


# In[32]:


df_sini.to_feather("siniestros_x_cif_id.feather")


# In[33]:


df_sini.shape

