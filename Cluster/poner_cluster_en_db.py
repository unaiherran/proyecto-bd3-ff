from decimal import Decimal
from datetime import datetime, date, timedelta

import mysql.connector
from coordenadas_a_cluster import *
from secret import *

connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    passwd=db_passwd,
    database=db_database,
    port=db_port
)

modelo = load_model("camaras_cluster.joblib")



def poblar_cluster():
    lista = modelo.cluster_centers_.tolist()

    if connection.is_connected():
        cur = connection.cursor()
    i = 0
    for l in lista:
        longitud = l[0]
        latitud = l[1]

        sql = f'INSERT INTO Cluster (id_cluster,longitud, latitud) values ' \
                          f'({i}, {longitud}, {latitud});'

        cur.execute(sql)

        connection.commit()
        i += 1


def clusterizar_sensores():
    if connection.is_connected():
        cur = connection.cursor()
        q = "SELECT * FROM SensoresTrafico;"
        cur.execute(q)

        data = cur.fetchall()

        for d in data:
            print (d)
            id = d[0]
            longitud = d[5]
            latitud = d[6]

            cluster = coordenadas_a_cluster(longitud, latitud, modelo)

            sql = f'UPDATE SensoresTrafico SET cluster = {cluster} WHERE id = {id};'

            cur.execute(sql)

            connection.commit()

            print(id, cluster, cur.rowcount, "records affected")


def clusterizar_camaras():
    if connection.is_connected():
        cur = connection.cursor()
        q = "SELECT * FROM CamarasTrafico;"
        cur.execute(q)

        data = cur.fetchall()

        for d in data:
            print(d)
            id = d[0]
            longitud = d[5]
            latitud = d[6]

            cluster = coordenadas_a_cluster(longitud, latitud, modelo)

            sql = f'UPDATE CamarasTrafico SET cluster = {cluster} WHERE id_camara = {id};'

            cur.execute(sql)

            connection.commit()

            print(id, cluster, cur.rowcount, "records affected")


def main():
    clusterizar_camaras()


if __name__ == '__main__':
    main()