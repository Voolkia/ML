
# coding: utf-8

# In[1]:


import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 500)


# In[2]:


table = "TB_INTERACCIONES_1a.tsv"
location = "../../data/raw"
sep = '\t'
encoding = 'latin1'
decimal = ','


# In[3]:


usable_cols = ['ID',
    'CIF_ID',
    'FECHA',
    'IN_OUT']


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


c_to_check = ["ID","CIF_ID"]


# *Cleaning weird values in ID and CIF_ID* 

# In[6]:


df = df[~pd.to_numeric(df['ID'], errors='coerce').isnull()]


# In[7]:


to_check = []
for val in df["CIF_ID"].unique():
    try:
        float(val)
    except Exception as e:
        print(e)
        to_check.append(val)


# In[8]:


df = df[~df["CIF_ID"].isin(to_check)]


# In[9]:


df["CIF_ID"].isna().sum()


# In[10]:


df["ID"].isna().sum()


# In[11]:


to_check = []
for val in df["ID"].unique():
    try:
        int(val)
    except Exception as e:
        print(e)
        to_check.append(val)


# In[12]:


df = df[~df["ID"].isin(to_check)]


# In[13]:


df = df.drop(columns='ID').astype({'CIF_ID': 'float64'})


# In[14]:


df.reset_index(drop=True).to_feather("interacciones.feather")


# In[15]:


df.shape


# In[16]:


df['CIF_ID'].nunique()

