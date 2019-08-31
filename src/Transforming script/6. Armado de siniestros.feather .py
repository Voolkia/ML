
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# In[2]:


table = "DSS_SINIESTROS_AUTO_1A.tsv"
location = "../../data/raw"
sep = '\t'
encoding = 'latin1'
decimal = ','


# ## Selecting columns to use

# In[3]:


usable_cols = ["NUM_SECU_POL",
    "MODELO_VEHICULO",
    "FEC_DENU_SINI",
    "FECHA_LIQUIDACION",
    "FECHA_RECHAZO"]


# ## Creating siniestros.feahter

# In[4]:


df = pd.read_csv(f"{location}/{table}",
                     sep=sep,
                     encoding=encoding,
                     decimal=decimal,
                     usecols = usable_cols)


# In[5]:


df.shape


# In[6]:


df.dtypes


# In[7]:


def lookup(s):
    dates = {date:pd.to_datetime(date, format="%d/%m/%Y") for date in s.unique()}
    return s.map(dates)

for fecha in [col for col in df.columns if "FEC" in col]:
    df[fecha] = lookup(df[fecha])


# In[8]:


df.dtypes


# In[9]:


data = {col: [df[col].min(),df[col].max()] for col in [col for col in df.columns if "FEC" in col]}
pd.DataFrame(data, index =['MIN', 'MAX'])


# In[10]:


for fecha in [col for col in df.columns if "FEC" in col]:
    df[fecha] = df[fecha].dt.strftime('%Y-%m')


# In[11]:


df[df["FEC_DENU_SINI"] > '2018-10']["FEC_DENU_SINI"].value_counts()


# In[12]:


df[df["FEC_DENU_SINI"] > '2018-10'].reset_index(drop=True).to_feather("siniestros.feather")

