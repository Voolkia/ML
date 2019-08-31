
# coding: utf-8

# In[1]:


import pandas as pd
import re


# ## Armado de dataset para entrenamiento del modelo

# In[2]:


df = pd.read_feather('../../data/processed/merged_data_13_periods.feather')


# In[3]:


df.shape


# ### Detectamos inconsistencias: (Ej. Del periodo 1 a 3 no hay cargados valores para SITUACION_PP

# <h4 style="color:red" > Se soluciona agregando las columnas al dataframe</h4>

# In[4]:


periodic_cols = set([''.join([s for s in col if not s.isdigit()]) for col in df[[col for col in df.columns if re.search(f'\d', col)]].columns])
periodic_cols


# In[5]:


to_check = ['_COBRO_BA',
 '_COBRO_CC',
 '_COBRO_PP',
 '_COBRO_SJ',
 '_COBRO_TA',
 '_SITUACION_AM',
 '_SITUACION_CT',
 '_SITUACION_EP',
 '_SITUACION_PP',
 '_TIPOINT_A',
 '_TIPOINT_I',
 '_TIPOINT_O']


# In[6]:


import numpy as np

for i in range(1,13):
    for col in to_check:
        if(f'{i}{col}' not in df.columns):
            print(f'adding {i}{col}')
            df[f'{i}{col}'] = np.nan


# ### Script de agrupación de registros de acuerdo a las ventanas temporales. El test está en *1. Test to arrange datasets by time periods*

# In[7]:


churn = 1
total_periods = 13

# Buscamos las features que son periódicas
periodic_cols = set([''.join([s for s in col if not s.isdigit()]) for col in df[[col for col in df.columns if re.search(f'\d', col)]].columns])

# Armamos otro dataframe con todas las features que no son temporales
non_periodic_df = df[[col for col in df.columns if not any(char.isdigit() for char in col)]]

# Definimos ventana inicial
w_low = 1
w_top = 6

final_df = pd.DataFrame()

while(w_top <= (total_periods-churn-2)):
    print(f"----------TIME WINDOW: {w_low} a {w_top}-----------")
    # Armamos todo el nuevo dataset del periodo en grouped_df
    grouped_df = non_periodic_df.copy(deep=True)

    #Seleccionamos las features del periodo
    print("Seleccionando features por periodo...                       ", end="\r", flush=True)
    for pcol in periodic_cols:
        regex_range = "|".join([str(i) for i in range(w_low, w_top+1)])
        regex = f'{pcol}({regex_range})$|^({regex_range}){pcol}'
        columns = [col for col in df.columns if re.search(regex, col)]
        grouped_df[[f"{i}_{pcol}" for i in range(6, 0, -1)]] = df[columns]

    # Buscamos los clientes que no tienen polizas en el periodo analizado
    print("Buscando clientes sin polizas...                       ", end="\r", flush=True)
    grouped_df = grouped_df[grouped_df["hist_polizas"].str.split(" ", expand=True).iloc[:,w_low-1:w_top].astype(float).sum(axis=1) > 0]
    
    # Buscamos las polizas que ya se dieron de baja en el periodo analizado
    print("Buscando clientes que ya se dieron de baja...                  ", end="\r", flush=True)
    grouped_df = grouped_df[~grouped_df["periodo_baja"].between(1, w_top + churn-1)]

    # Preparamos columnas de pólizas por período
    print("Preparando pólizas por períodos...                             ", end="\r", flush=True)
    grouped_df[[f"polizas_{i}" for i in range(6, 0, -1)]] = grouped_df["hist_polizas"].str.split(" ", expand=True).iloc[:,w_low-1:w_top].astype(float)
    
    # Calculamos campos adicionales (Diferencias entre periodos)
    print("Preparando campos adicionales...                             ", end="\r", flush=True)
    for i in range(5, 0, -1):
        grouped_df[f"diff_cant_polizas_{i}"] = grouped_df[f"polizas_{i}"] - grouped_df[f"polizas_{i+1}"]    
        current_int = [col for col in grouped_df.columns if re.search(f'({i})__TIPOINT', col)]
        next_int = [col for col in grouped_df.columns if re.search(f'({i+1})__TIPOINT', col)]
        grouped_df[f"diff_cant_int_{i}"] =  grouped_df[current_int].sum(axis=1) - grouped_df[next_int].sum(axis=1)
        
    # Marcamos aquellos que se dieron de baja a los cuatro meses del periodo analizado
    print("Creando flag de baja...                             ", end="\r", flush=True)
    grouped_df[f"BAJA_{churn}m"] = grouped_df["periodo_baja"] == (w_top + churn)

    # Marcamos un flag para saber la ventana de tiempo que se analiza
    print("Creando flag de periodo...                        ", end="\r", flush=True)
    grouped_df["time_window"] = f"{w_low} a {w_top}"

    # Agregamos el tipo de dataset
    # 1 to validation
    # 1 to optimization
    # rest to train
    
    if(w_top > (total_periods-churn-3)):
        grouped_df["dataset"] = 'val'
    elif(w_top > (total_periods-churn-4)):
        grouped_df["dataset"] = 'opt'
    else:
        grouped_df["dataset"] = 'train'
    
    # Agregamos el periodo al datafame final 
    final_df = pd.concat([final_df, grouped_df], ignore_index=True)
    
    del grouped_df
    w_low += 1
    w_top += 1
    print("Next window...                        ")
    
    
del non_periodic_df
print("Ready!")


# In[8]:


final_df.shape


# In[9]:


final_df['dataset'].value_counts()


# In[10]:


final_df[final_df['BAJA_1m']].tail(5)


# Una vez verificados los datos, eliminamos las columnas que no se van a usar más

# In[11]:


final_df = final_df.drop(["time_window","hist_polizas","periodo_baja"], axis=1)


# ## Guardamos los datsets

# ### Train

# In[12]:


final_df[final_df['dataset'] == 'train'].drop(columns='dataset').reset_index(drop=True).to_feather(f"../../data/processed/Churn_{churn}_train_set.feather")


# ### Opt

# In[13]:


final_df[final_df['dataset'] == 'opt'].drop(columns='dataset').reset_index(drop=True).to_feather(f"../../data/processed/Churn_{churn}_optimization_set.feather")


# ### Val

# In[14]:


final_df[final_df['dataset'] == 'val'].drop(columns='dataset').reset_index(drop=True).to_feather(f"../../data/processed/Churn_{churn}_validation_set.feather")

