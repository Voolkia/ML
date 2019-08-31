
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# ### Lectura de polizas.feather

# In[2]:


df_polizas = pd.read_feather('../../data/interim/polizas.feather')


# In[3]:


df_polizas.nunique()


# In[4]:


df_polizas.dtypes


# In[5]:


df_polizas['FECHA_VIG_POL'] = df_polizas['FECHA_VIG_POL'].map({date: pd.to_datetime(date, format="%d/%m/%Y") for date in df_polizas['FECHA_VIG_POL'].unique()})


# In[6]:


data = {col: [df_polizas[col].min(),df_polizas[col].max()] for col in ['FECHA_VIG_POL']}
pd.DataFrame(data, index =['MIN', 'MAX'])


# *Calculamos mes y año de vigencia*

# In[7]:


df_polizas['mes_anio_vig'] = df_polizas['FECHA_VIG_POL'].dt.strftime('%Y-%m')


# In[8]:


sorted(df_polizas['mes_anio_vig'].unique())


# *Filtramos las columnas para hacer el pivot por CIF_ID*

# In[9]:


to_pivot = df_polizas[["CIF_ID","NUM_SECU_POL","MCA_VIGENCIA","mes_anio_vig"]].drop_duplicates() 


# In[10]:


df_polizas_pivoted = to_pivot.pivot_table(index='CIF_ID',columns=['mes_anio_vig'], values=['MCA_VIGENCIA'],aggfunc='count',fill_value=0)


# In[11]:


df_polizas_pivoted.head(5)


# In[12]:


df_polizas_pivoted = df_polizas_pivoted.iloc[:,-18:]


# In[13]:


df_polizas_pivoted = df_polizas_pivoted.astype(str)


# In[14]:


df_polizas_pivoted["history"] = df_polizas_pivoted.apply(" ".join, axis=1)


# In[15]:


def simplify(x):
    return "".join(["1" if int(n)>0 else "0" for n in x.split(" ")])

df_polizas_pivoted["boolean_history"] = df_polizas_pivoted["history"].apply(simplify).values


# In[16]:


df_polizas_pivoted.head(5)


# *Filtramos aquellos registros que nunca tienen polizas vigentes en el periodo analizado*

# In[17]:


df_polizas_pivoted[df_polizas_pivoted["history"] == "0 0 0 0 0 0 0 0 0 0 0 0 0"].head()


# In[18]:


df_polizas_pivoted = df_polizas_pivoted[df_polizas_pivoted["history"] != "0 0 0 0 0 0 0 0 0 0 0 0 0"]


# *Ahora buscamos bajas y el periodo en el cual se detectan tres polizas seguidas sin vigencia*

# In[19]:


df_polizas_pivoted["periodo_baja"] = -1


# In[20]:


df_polizas_pivoted.loc[df_polizas_pivoted["periodo_baja"] == -1, "periodo_baja"] =df_polizas_pivoted.loc[df_polizas_pivoted["periodo_baja"] == -1, "boolean_history"].str.find(f'1000').values


# In[21]:


df_polizas_pivoted.loc[df_polizas_pivoted["periodo_baja"] > -1,"periodo_baja"] =df_polizas_pivoted.loc[df_polizas_pivoted["periodo_baja"] > -1,"periodo_baja"] + 2 


# **Just for checking:** observamos las bajas detectadas

# In[22]:


df_polizas_pivoted[df_polizas_pivoted["periodo_baja"] > -1].head(15)


# In[23]:


df_bajas = pd.DataFrame(df_polizas_pivoted.index)


# In[24]:


df_bajas = df_bajas.set_index('CIF_ID')


# In[25]:


df_bajas["hist_polizas"] = df_polizas_pivoted["history"]
df_bajas["periodo_baja"] = df_polizas_pivoted["periodo_baja"]


# In[26]:


df_bajas


# In[27]:


len(df_bajas)


# In[28]:


df_bajas.reset_index().to_feather('../../data/processed/periodos_baja_x_cif_id.feather')

