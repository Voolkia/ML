
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# ## Importamos los archivos

# In[2]:


df_bajas = pd.read_feather('../../data/processed/periodos_baja_x_cif_id.feather')


# In[3]:


df_pagos = pd.read_feather('../../data/processed/pagos_x_cif_id.feather')


# In[4]:


df_interacciones = pd.read_feather('../../data/processed/interacciones_tipo_periodo_x_cif_id.feather')


# In[5]:


df_clientes = pd.read_feather('../../data/interim/clientes.feather')


# In[6]:


df_clientes = df_clientes.rename(columns={"ID":"CIF_ID"})


# In[7]:


df_siniestros = pd.read_feather('../../data/processed/siniestros_x_cif_id.feather')


# ## Verificamos que todos se puedan combinar con la tabla Bajas

# In[8]:


def check_merge(df1,df2,field):
    return len(set(df1[field].unique()).intersection(set(df2[field].unique()))) / len(df1[field].unique())


# In[9]:


df_pagos.columns


# In[10]:


check_merge(df_bajas, df_pagos, "CIF_ID")


# In[11]:


check_merge(df_bajas, df_clientes, "CIF_ID")


# In[12]:


check_merge(df_bajas, df_interacciones, "CIF_ID")


# In[13]:


check_merge(df_bajas, df_siniestros, "CIF_ID")


# ## Merge entre tablas

# In[14]:


len(df_bajas)


# In[15]:


len(df_interacciones)


# In[16]:


len(df_pagos)


# In[17]:


len(df_clientes)


# In[18]:


len(df_siniestros)


# In[19]:


df_bajas_int =  pd.merge(df_bajas, df_interacciones, on=['CIF_ID'], how='left')


# In[20]:


df_bajas_int.head()


# In[21]:


df_bajas_int_sini =  pd.merge(df_bajas_int, df_siniestros, on=['CIF_ID'], how='left')


# In[22]:


df_bajas_int_sini = df_bajas_int_sini.fillna(0)


# In[23]:


df_bajas_int_sini.head()


# In[24]:


from functools import reduce
df_merged = reduce(lambda  left,right: pd.merge(left, right, on=['CIF_ID'], how='inner'), [df_bajas_int_sini, df_pagos, df_clientes])


# In[25]:


df_merged.shape


# ### Guardamos la tabla completa

# In[26]:


df_merged.to_feather('../../data/processed/merged_data_13_periods.feather')


# --- 

# In[27]:


"], [".join(set([''.join([s for s in col if not s.isdigit()]) for col in df_merged.columns]))

