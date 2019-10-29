import logging
import math

import mysql.connector
import pandas as pd

from config import *

logging.basicConfig(level=logging.INFO, filemode='a', format='%(asctime)s - %(message)s')

if __name__ == "__main__":
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_database,
        port=db_port
    )

    if connection.is_connected():
        cursor = connection.cursor()

        df = pd.read_csv('pmed_ubicacion_09-2019.csv', delimiter=',')

        for index, row in df.iterrows():
            if row.get('tipo_elem') == 'URB':
                tipo_elem = 0
            else:
                tipo_elem = 1

            if math.isnan(row.get('distrito', 0)):
                distrito = -1
            else:
                distrito = row.get('distrito')

            print(row)
            sql = f'INSERT INTO SensoresTrafico(tipo_elem, distrito, id, cod_cent, nombre, utm_x, utm_y, longitud, latitud) \
            VALUES ({tipo_elem}, {distrito}, {row.get("id")}, \'{row.get("cod_cent")}\', \'{row.get("nombre")}\', {row.get("utm_x")}, {row.get("utm_y")}, {row.get("longitud")}, {row.get("latitud")});'
            print(sql)
            cursor.execute(sql)
        # close the connection to the database.
        connection.commit()
        cursor.close()
        print("Done")
