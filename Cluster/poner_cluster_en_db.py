from decimal import Decimal
from datetime import datetime, date, timedelta

import mysql.connector
from coordenadas_a_cluster import *
from secret import *
import pandas as pd
from sklearn.cluster import KMeans

connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    passwd=db_passwd,
    database=db_database,
    port=db_port
)

modelo = load_model("recluster.joblib")


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
        q = "SELECT id, longitud, latitud FROM SensoresTrafico;"
        cur.execute(q)

        data = cur.fetchall()

        for d in data:
            print (d)
            id = d[0]
            longitud = d[1]
            latitud = d[2]

            cluster = coordenadas_a_cluster(longitud, latitud, modelo)

            sql = f'UPDATE SensoresTrafico SET cluster = {cluster} WHERE id = {id};'

            cur.execute(sql)

            connection.commit()

            print(id, cluster, longitud, latitud, cur.rowcount, "records affected")


def clusterizar_eventos():
    if connection.is_connected():
        cur = connection.cursor()
        q = "SELECT id, longitud, latitud FROM DatosEventos;"
        cur.execute(q)

        data = cur.fetchall()

        for d in data:

            id = d[0]
            longitud = d[1]
            latitud = d[2]

            cluster = coordenadas_a_cluster(longitud, latitud, modelo)

            sql = f'UPDATE DatosEventos SET cluster = {cluster} WHERE id = {id};'

            cur.execute(sql)

            connection.commit()

            print(id, cluster, longitud, latitud, cur.rowcount, "records affected")



def clusterizar_camaras():
    if connection.is_connected():
        cur = connection.cursor()
        q = "SELECT * FROM CamarasTrafico;"
        cur.execute(q)

        data = cur.fetchall()

        for d in data:

            id = d[0]
            longitud = d[2]
            latitud = d[3]

            cluster = coordenadas_a_cluster(longitud, latitud, modelo)

            sql = f'UPDATE CamarasTrafico SET cluster = {cluster} WHERE id_camara = {id};'

            cur.execute(sql)

            connection.commit()

            print(id, cluster)


def contaminacion_a_cluster():
    if connection.is_connected():
        q = "SELECT longitud, latitud FROM contaminacion_estacion;"
        df = pd.read_sql(q, connection)
        print(df.columns)
        X_contaminacion = df.drop(columns=['id']).values
        num_cluster_cont = 24
        random_state = 42
        kmeans_contaminacion = KMeans(n_clusters=num_cluster_cont, random_state=random_state)
        y_pred_contaminacion = kmeans_contaminacion.fit(X_contaminacion)

        cur = connection.cursor()
        q = "SELECT id_cluster, longitud, latitud FROM Clusters;"
        cur.execute(q)

        cluster = cur.fetchall()

        for c in cluster:
            id = c[0]
            long = c[1]
            lat = c[2]
            coordenadas = np.array([long, lat])

            sensor = y_pred_contaminacion.predict(X=coordenadas.reshape(1, -1))[0]

            sql = f'UPDATE Cluster SET contaminacion = {sensor} WHERE id_cluster = {id}'
        i = 0
        for l in lista:
            longitud = l[0]
            latitud = l[1]

            sql = f'INSERT INTO Cluster (id_cluster,longitud, latitud) values ' \
                  f'({i}, {longitud}, {latitud});'

            cur.execute(sql)

            connection.commit()
            i += 1




def main():
    # clusterizar_camaras()
    # clusterizar_sensores()
    #clusterizar_eventos()
    contaminacion_a_cluster()



if __name__ == '__main__':
    main()