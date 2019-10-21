#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from datetime import datetime
from datetime import timedelta 


# In[18]:


#!wget https://www.dropbox.com/s/1wnnyvfof600y74/300107-0-agenda-actividades-eventos.csv
#!ls -l


# In[2]:


eventos_df = pd.read_csv('300107-0-agenda-actividades-eventos.csv', encoding = 'ISO-8859-1', sep=';', engine='python')
eventos_df.head(5)


# In[3]:


print(eventos_df.shape)
eventos_reduced_df = eventos_df[['TITULO', 'GRATUITO', 'DIAS-SEMANA', 'FECHA', 'FECHA-FIN', 'HORA', 'LATITUD', 'LONGITUD']]


# In[4]:


eventos_reduced_df.tail(5)


# In[5]:


print('Limpiamos el dataset de elementos que no tengan los campos obligatorios')
eventos_reduced_df = eventos_reduced_df.dropna(subset=['HORA', 'LATITUD', 'LONGITUD', 'FECHA', 'FECHA-FIN'])
eventos_reduced_df.tail(10)


# In[6]:


print(eventos_reduced_df.shape)


# In[7]:


eventos_reduced_df['FECHA'] = pd.to_datetime(eventos_reduced_df['FECHA'])
eventos_reduced_df['FECHA-FIN'] = pd.to_datetime(eventos_reduced_df['FECHA-FIN'])


# In[19]:



dias_semana = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

eventos_final = []

for _, row in eventos_reduced_df.iterrows():
    
    fecha = row['FECHA']
    fecha_fin = row['FECHA-FIN']
    fecha_day = row['FECHA'].day
    fecha_month = row['FECHA'].month
    fecha_year = row['FECHA'].year
    fecha_fin_day = row['FECHA-FIN'].day
    fecha_fin_month = row['FECHA-FIN'].month
    fecha_fin_year = row['FECHA-FIN'].year
    dias_semana_evento = row['DIAS-SEMANA']
    
    hora_evento = row['HORA'].split(':')    
    
    # Transformar cada evento con su timestamp de cuándo comienza el evento
    fecha = fecha.replace(hour=int(hora_evento[0]), minute=int(hora_evento[1]), second=0, microsecond=0)

    print('fecha_evento:\t\t' + str(fecha))
    print('fecha_fin_evento:\t' + str(fecha_fin))
    print('dias_semana_evento:\t' + str(dias_semana_evento))
    print('\n')

    if (fecha_day != fecha_fin_day or fecha_month != fecha_fin_month or fecha_year != fecha_fin_year):

        # Generamos tantos eventos como días toquen según la programación de 'DIAS-SEMANA'
        while fecha < fecha_fin:

            dia_semana = dias_semana[fecha.weekday()]
            
            # Si el día tiene evento, lo generamos y guardamos en el array
            if (dia_semana in dias_semana_evento):
                #print('este día hay evento\n')
                evento_nuevo = {}
            
                evento_nuevo['TITULO'] = row['TITULO']
                evento_nuevo['GRATUITO'] = row['GRATUITO']
                evento_nuevo['FECHA'] = fecha
                evento_nuevo['FECHA-FIN'] = row['FECHA-FIN']
                evento_nuevo['HORA'] = row['HORA']
                evento_nuevo['LATITUD'] = row['LATITUD']
                evento_nuevo['LONGITUD'] = row['LONGITUD']
                
                eventos_final.append(evento_nuevo)

            fecha = fecha + timedelta(days = 1)
    else:
        evento_nuevo = {}
        
        evento_nuevo['TITULO'] = row['TITULO']
        evento_nuevo['GRATUITO'] = row['GRATUITO']
        evento_nuevo['FECHA'] = fecha
        evento_nuevo['FECHA-FIN'] = row['FECHA-FIN']
        evento_nuevo['HORA'] = row['HORA']
        evento_nuevo['LATITUD'] = row['LATITUD']
        evento_nuevo['LONGITUD'] = row['LONGITUD']

        eventos_final.append(evento_nuevo)


eventos_final_df = pd.DataFrame(eventos_final)
    
    


# In[9]:


eventos_final_df.shape


# In[12]:


eventos_final_df.head(5)


# In[11]:


eventos_final_df.tail(5)


# In[13]:


#pip install mysql-connector-python

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from config import *


# In[16]:



if __name__ == "__main__":
    
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            passwd=db_passwd,
            database=db_database,
            port=db_port
        )

        cursor = connection.cursor()
        
        for _, row in eventos_final_df.iterrows():
            print(row)
            sql = f'INSERT INTO DatosEventos(fecha, gratuito, titulo, longitud, latitud)             VALUES             (\'{row.get("FECHA")}\', {row.get("GRATUITO")}, \'{row.get("TITULO")}\', {row.get("LONGITUD")}, {row.get("LATITUD")});'
            print(sql)
            cursor.execute(sql)

        connection.commit()
        print("Records inserted successfully into DatosEventos table")
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into DatosEventos table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()
            print("MySQL connection is closed")


# In[ ]:





# In[ ]:




