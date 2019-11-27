from secret import *
import mysql.connector
import pandas as pd


df = pd.read_csv('lista_camaras.csv', delimiter=',')

connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    passwd=db_passwd,
    database=db_database,
    port=db_port
)

if connection.is_connected():
    cursor = connection.cursor()

    df = pd.read_csv('lista_camaras.csv', delimiter=',')

    for index, row in df.iterrows():

        if row[2] == 'S':
            foto = True
            video = False
        else:
            foto = False
            video = True

        sql = f'INSERT INTO CamarasTrafico(id_camara,feed,longitud,latitud,video,foto) VALUES' \
             f'({row[0]}, "{row[1]}", {row[3]}, {row[4]}, {video}, {foto});'

        print(sql)
        cursor.execute(sql)

    # close the connection to the database.
    connection.commit()
    cursor.close()
    print("Done")