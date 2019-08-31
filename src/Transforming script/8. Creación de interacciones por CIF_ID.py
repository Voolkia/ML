
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# ## Analizamos cómo agrupar interacciones por CIF_ID

# In[2]:


df = pd.read_feather("interacciones.feather")


# In[3]:


df.head(5)


# In[4]:


df["IN_OUT"].value_counts(dropna=False)


# In[5]:


df = df[df["IN_OUT"].isin(['O','I','A'])]


# In[6]:


df["FECHA"] = df["FECHA"].str.slice(stop=10) 


# In[7]:


df.loc[df["FECHA"].str.contains(" [0-9]", na=False), "FECHA"] = df.loc[df["FECHA"].str.contains(" [0-9]", na=False), "FECHA"].str.slice(stop=8) 


# In[8]:


df["FECHA"] = df["FECHA"].str.replace(" ","")


# In[9]:


def to_date(s):
    dates = {date:pd.to_datetime(date, format="%d/%m/%Y") for date in s.unique()}
    return s.map(dates)

df["periodo"] = to_date(df["FECHA"])


# Transformamos la fecha en anio y mes

# In[10]:


def to_yearmonth(s):
    dates = {date:pd.Timestamp(date).strftime('%Y-%m') for date in s.unique()}
    return s.map(dates)

df["periodo"] = to_yearmonth(df["periodo"].dropna())


# In[11]:


df["periodo"].value_counts().sort_index().plot.bar()


# In[12]:


data = {fecha:i + 1 for i,fecha in enumerate(df["periodo"].unique())}
data


# In[13]:


df["periodo_int"] = df["periodo"].map(data)


# In[14]:


df = df[df["periodo_int"] < 19]


# In[15]:


df.head()


# In[16]:


to_pivot = df[["CIF_ID","IN_OUT","periodo_int"]]


# In[17]:


pivoted = to_pivot.pivot_table(index=["CIF_ID"], columns=["periodo_int","IN_OUT"], aggfunc="size")
pivoted


# In[18]:


df_interacciones = pd.DataFrame(pivoted.to_records())


# In[19]:


df_interacciones = df_interacciones.rename(columns=lambda x: x.replace("(","").replace(")","").replace(", ","_TIPOINT_").replace("'","")) 


# In[20]:


df_interacciones.reset_index(drop=True).to_feather("interacciones_tipo_periodo_x_cif_id.feather")


# In[21]:


df_interacciones.shape

