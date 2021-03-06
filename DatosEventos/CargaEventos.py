#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from datetime import timedelta

from coordenadas_a_cluster import *

modelo = load_model("kmeans.21.3.joblib")


# In[2]:


#!ls -l
#!rm 300107-0-agenda-actividades-eventos.csv
#!ls -l
#!wget https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.csv
#!ls -l


# In[3]:


#eventos_df = pd.read_csv('300107-0-agenda-actividades-eventos.csv', encoding = 'ISO-8859-1', sep=';', engine='python')
#eventos_df.head(5)


# In[4]:



url_agenda_eventos = "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.csv"

response = requests.get(url_agenda_eventos, headers={"User-Agent": "curl/7.61.0"})

data = StringIO(response.content.decode('ISO-8859-1'))

eventos_df = pd.read_csv(data, sep=';', engine='python')
eventos_df.head(5)


# In[5]:


print(eventos_df.shape)
eventos_reduced_df = eventos_df[['TITULO', 'GRATUITO', 'DIAS-SEMANA', 'FECHA', 'FECHA-FIN', 'HORA', 'LATITUD', 'LONGITUD']]


# In[6]:



eventos_reduced_df.tail(5)


# In[7]:


print('Limpiamos el dataset de elementos que no tengan los campos obligatorios')
eventos_reduced_df = eventos_reduced_df.dropna(subset=['HORA', 'LATITUD', 'LONGITUD', 'FECHA', 'FECHA-FIN'])

eventos_reduced_df = eventos_reduced_df.drop(eventos_reduced_df[eventos_reduced_df['HORA'] == '00:00'].index)
eventos_reduced_df.tail(10)


# In[8]:


print(eventos_reduced_df.shape)


# In[9]:


eventos_reduced_df['FECHA'] = pd.to_datetime(eventos_reduced_df['FECHA'])
eventos_reduced_df['FECHA-FIN'] = pd.to_datetime(eventos_reduced_df['FECHA-FIN'])


# In[10]:



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
                evento_nuevo['CLUSTER'] = coordenadas_a_cluster(row['LONGITUD'], row['LATITUD'], modelo)
                
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
        evento_nuevo['CLUSTER'] = coordenadas_a_cluster(row['LONGITUD'], row['LATITUD'], modelo)

        eventos_final.append(evento_nuevo)


eventos_final_df = pd.DataFrame(eventos_final)
    
    


# In[11]:


eventos_final_df.shape


# In[12]:


eventos_final_df.head(5)


# In[13]:


eventos_final_df.tail(5)


# In[14]:


#pip install mysql-connector-python

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from config import *


# In[ ]:



if __name__ == "__main__":
    
    nuevos = 0
    existentes = 0
    
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
            #print(row)
            sql = f'INSERT INTO DatosEventos(fecha, gratuito, titulo, longitud, latitud, cluster)             VALUES             (\'{row.get("FECHA")}\', {row.get("GRATUITO")}, \"{row.get("TITULO")}\", {row.get("LONGITUD")}, {row.get("LATITUD")}, {row.get("CLUSTER")});'
            #print(sql)
            try:
                cursor.execute(sql)
                nuevos = nuevos + 1
            except mysql.connector.Error as err:
                existentes = existentes + 1
                print("Error: {}".format(err))

        connection.commit()
        print("Records inserted successfully into DatosEventos table")
        sql_count = f'SELECT COUNT(*) FROM DatosEventos;'
        cursor.execute(sql_count)
        total_eventos = cursor.fetchone()
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into DatosEventos table {}".format(error))

    finally:
        if (connection.is_connected()):
            connection.close()
            print("MySQL connection is closed")
    print("\tnuevos: " + str(nuevos))
    print("\texistentes: " + str(existentes))
    text = "Proceso de Carga de Eventos finalizado. \n\tTotal en CSV: {0}\n\tYa cargados en BD: {1}\n\tNuevos: {2}\n\tTotal Eventos en BD: {3}".format(str(eventos_final_df.shape[0]), str(existentes), str(nuevos), str(total_eventos[0]))
    payload = {'chat_id': tg_group, 'text': text}
    print(text)
    requests.post(tg_url, data=payload)
print("-----------\n")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




