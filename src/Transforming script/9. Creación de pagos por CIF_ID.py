
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# In[2]:


df = pd.read_feather("../../data/interim/pagos.feather")


# In[3]:


df.head(5)


# In[4]:


df_id_pol = pd.read_feather("../../data/interim/poliza_x_cliente.feather")


# In[5]:


len(set(df_id_pol["NUM_SECU_POL"].unique()).intersection(set(df["NUM_SECU_POL"].unique()))) / len(df["NUM_SECU_POL"].unique())


# In[6]:


df["NUM_SECU_POL"].nunique()


# Usamos un inner join para unirlas ya que no nos sirven los campos que no tengan cif_id

# In[7]:


df = pd.merge(df, df_id_pol, on='NUM_SECU_POL', how='inner')


# **Revisamos los pagos**

# In[8]:


df.nunique()


# Removemos pagos que esten por fuera del periodo a analizar

# In[9]:


df = df.loc[~df["FECHA_VTO"].str.contains("20[12][067]")]


# In[10]:


df = df.loc[~df["FECHA_VTO"].str.contains("2018-0")]


# In[11]:


df = df.loc[~df["FECHA_VTO"].str.contains("2018-10")]


# In[12]:


df = df.loc[~df["FECHA_VTO"].str.contains("2019-12")]


# In[13]:


df["FECHA_VTO"].value_counts().sort_index().plot.bar()


# Revisamos algunas estadisticas de nuevo

# In[14]:


df.nunique()


# ### Generamos algunas variables adicionales

# #### Diferencia entre fecha de pago y vencimiento
# - [PAGO - VENCIMIENTO]

# In[15]:


def lookup(s):
    """
    This is an extremely fast approach to datetime parsing.
    For large data, the same dates are often repeated. Rather than
    re-parse these, we store all unique dates, parse them, and
    use a lookup to convert all dates.
    """
    dates = {date:pd.to_datetime(date) for date in s.unique()}
    return s.map(dates)

df["FECHA_VTO"] = lookup(df["FECHA_VTO"])
df["FEC_PAGO"] = lookup(df["FEC_PAGO"])


# In[16]:


import numpy as np
df["demora_pago"] = ((df["FEC_PAGO"] - df["FECHA_VTO"])/np.timedelta64(1, 'M')).astype("float")


# In[17]:


df[["demora_pago","FECHA_VTO","FEC_PAGO"]] 


# In[18]:


df["demora_pago"].value_counts()


# In[19]:


print(df["demora_pago"].min(),df["demora_pago"].max()) 


# #### Revisamos COD_COBRO

# In[20]:


df["COD_COBRO"].value_counts(dropna=False)


# Según el diccionario de datos TM/TA = Tarjeta así que los unificamos en TA

# In[21]:


df.loc[df["COD_COBRO"]=="TM","COD_COBRO"] = "TA"


# In[22]:


df["COD_COBRO"].value_counts(dropna=False)


# #### Creamos la variable periodo en lugar de fecha_vto para que coincida con el resto de las tablas

# In[23]:


new_data = {fecha:pd.to_datetime(fecha).strftime('%Y-%m') for fecha in df["FECHA_VTO"].unique()}
new_data


# In[24]:


df["FECHA_VTO"] = df["FECHA_VTO"].map(new_data)


# In[25]:


data = {fecha:i + 1 for i,fecha in enumerate(sorted(df["FECHA_VTO"].unique()))}
data


# In[26]:


df["periodo"] = df["FECHA_VTO"].map(data)


# In[27]:


df.head()


# #### Empezamos a probar pivots por CIF_ID

# In[28]:


df = df.rename(columns={"diferencia_vto_pago": "demora_pago"})


# In[29]:


to_pivot = df[["CIF_ID","demora_pago","periodo","COD_COBRO","COD_SITUACION","MONTO_PAGO"]]


# In[30]:


df_pagos_datediff = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo"], values=["demora_pago","MONTO_PAGO"], aggfunc="mean")


# In[31]:


df_pagos_datediff.head()


# In[32]:


df_cods = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo","COD_SITUACION"], aggfunc="size")
df_cods.head()


# In[33]:


df_codc = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo","COD_COBRO"], aggfunc="size")
df_codc.head()


# *Formateamos los DataFrames para unirlos en uno solo*

# In[34]:


df_pagos_datediff = pd.DataFrame(df_pagos_datediff.to_records())
df_pagos_datediff.head()


# In[35]:


df_cods = pd.DataFrame(df_cods.to_records())
df_cods.head()


# In[36]:


df_codc = pd.DataFrame(df_codc.to_records())
df_codc.head()


# In[37]:


len(df_codc) == len(df_cods) == len(df_pagos_datediff)


# In[38]:


len(df_cods)


# ### Renombramos las columnas

# In[39]:


df_codc.columns


# In[40]:


df_codc = df_codc.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_COBRO_").replace("'",""))


# In[41]:


df_codc.columns


# In[42]:


df_cods.columns


# In[43]:


df_cods = df_cods.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_SITUACION_").replace("'",""))


# In[44]:


df_cods.columns


# In[45]:


df_pagos_datediff.columns


# In[46]:


df_pagos_datediff = df_pagos_datediff.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_").replace("'",""))


# In[47]:


df_pagos_datediff.columns


# ### Ahora unimos los dataframes

# In[48]:


del df
del to_pivot


# In[49]:


data = [df_cods,df_codc,df_pagos_datediff]
from functools import reduce


# In[50]:


df = reduce(lambda  left,right: pd.merge(left, right, on=['CIF_ID'], how='outer'), data)
len(df)


# In[51]:


sum([len(df.columns) for df in data])


# In[52]:


len(df.columns)


# In[53]:


len(set(df.columns))


# In[54]:


df["CIF_ID"].nunique()


# In[55]:


(df[[col for col in df.columns if "demora_pago" in col]] > 0).sum().plot.bar().set(xlabel="Periodos", ylabel="Pagos demorados")


# In[56]:


df[[col for col in df.columns if "demora_pago" in col]] = df[[col for col in df.columns if "demora_pago" in col]].fillna(999)


# In[59]:


df[[col for col in df.columns if "MONTO_PAGO" in col]] = df[[col for col in df.columns if "MONTO_PAGO" in col]].fillna(0)


# In[60]:


df.to_feather("../../data/processed/pagos_x_cif_id.feather")

