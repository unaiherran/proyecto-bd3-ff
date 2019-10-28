import logging

import mysql.connector

from config import *

logging.basicConfig(level=logging.INFO, filename='merger_realtime.log', filemode='a',
                    format='%(asctime)s - %(message)s')


def make_relations():
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_database,
        port=db_port
    )

    if connection.is_connected():
        cursor = connection.cursor()

        cursor.execute("SELECT id_camara, longitud, latitud FROM CamarasTrafico;")
        result = cursor.fetchall()

        for x in result:
            id = x[0]
            longitud = x[1]
            latitud = x[2]

            cursor_distance = connection.cursor()

            sql = f'''SELECT id, longitud, latitud,
            power(longitud - ({longitud}), 2) + power(latitud - ({latitud}), 2) distance 
            FROM SensoresTrafico             
            ORDER BY distance asc
            LIMIT 20'''

            sql = f'''
select id, longitud, latitud,  (acos(sin(radians({latitud})) * sin(radians(latitud)) + 
cos(radians({latitud})) * cos(radians(latitud)) * 
cos(radians({longitud}) - radians(longitud))) * 6378) * 1000 as distance
from SensoresTrafico
HAVING distance < 200
ORDER BY distance asc
'''
            print(sql)
            cursor_distance.execute(sql)

            result_distance = cursor_distance.fetchall()

            # print(result_distance[0][3])

            cursor_insert = connection.cursor()
            for r in result_distance:
                insert = f'''INSERT INTO CamarasSensores (id_camara, id_sensor, distancia)
VALUES ({id}, {r[0]}, {r[3]})'''
                cursor_insert.execute(insert)

            cursor_insert.close()
            connection.commit()


if __name__ == "__main__":
    make_relations()
