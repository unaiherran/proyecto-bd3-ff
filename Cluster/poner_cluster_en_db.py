from decimal import Decimal
from datetime import datetime, date, timedelta

import mysql.connector
from coordenadas_a_cluster import *
from secret import *
import pandas as pd
from sklearn.cluster import KMeans
import geopy.distance

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
        q = "SELECT id, longitud, latitud FROM contaminacion_estacion;"
        df = pd.read_sql(q, connection)
        X_contaminacion = df.drop(columns=['id']).values
        num_cluster_cont = 24
        random_state = 42
        kmeans_contaminacion = KMeans(n_clusters=num_cluster_cont, random_state=random_state)
        y_pred_contaminacion = kmeans_contaminacion.fit(X_contaminacion)

        cur = connection.cursor()
        q = "SELECT id_cluster, longitud, latitud FROM Cluster;"
        cur.execute(q)

        cluster = cur.fetchall()

        for c in cluster:
            id = c[0]
            long = c[1]
            lat = c[2]
            coordenadas = np.array([long, lat])

            sensor = y_pred_contaminacion.predict(X=coordenadas.reshape(1, -1))[0]

            sql = f'UPDATE Cluster SET contaminacion = {sensor} WHERE id_cluster = {id}'
            cur.execute(sql)

            connection.commit()

            print(id, sensor)


def clusterizar_gran_evento():
    if connection.is_connected():
        distancia = 1000

        cur = connection.cursor()
        q = "SELECT id, longitud, latitud FROM DatosGrandesEventos;"
        cur.execute(q)

        data = cur.fetchall()

        for d in data:

            id_evento = d[0]
            ge_lon = d[1]
            ge_lat = d[2]

            main_cluster = coordenadas_a_cluster(ge_lon, ge_lat, modelo)
            lista_clusters_cercanos = []

            q = "SELECT id_cluster, longitud, latitud FROM Cluster;"
            cur.execute(q)
            lista_clusters = cur.fetchall()
            coords_ge = (ge_lon, ge_lat)

            for clu in lista_clusters:
                coords_clu = (clu[1], clu[2])

                if clu[0] != main_cluster:
                    if geopy.distance.geodesic(coords_ge, coords_clu).m < distancia:
                        lista_clusters_cercanos.append(clu[0])

            near_clu = ' '.join([str(elem) for elem in lista_clusters_cercanos])

            sql = f'UPDATE DatosGrandesEventos SET cluster = {main_cluster}, clusters_cercanos = "{near_clu}" ' \
                  f'WHERE id = {id_evento};'

            cur.execute(sql)

            connection.commit()

            print(id, main_cluster, near_clu, cur.rowcount, "records affected")


def tiempo_a_cluster():
    # leer todas las estaciones
    if connection.is_connected():
        cur = connection.cursor()
        q = "SELECT id, longitud, latitud FROM EstacionTiempo;"
        cur.execute(q)
        estaciones_tiempo = cur.fetchall()

        # leer todos los clusters
        q = "SELECT id_cluster, longitud, latitud FROM Cluster;"
        cur.execute(q)

        clusters = cur.fetchall()

        for clu in clusters:
            # ver que estacion está más cerca de cada cluster
            distancia_estacion = 999999
            estacion = 99
            coord_clu = (clu[1], clu[2])
            for est in estaciones_tiempo:
                coord_est =(est[1], est[2])
                if geopy.distance.geodesic(coord_est, coord_clu).m < distancia_estacion:
                    distancia_estacion = geopy.distance.geodesic(coord_est, coord_clu).m
                    estacion = est[0]
            # Asignar
            print(f"Cluster {clu[0]} -> Estacion más cercana {estacion} a {distancia_estacion} m")

def main():
    pass
    # clusterizar_camaras()
    # clusterizar_sensores()
    # clusterizar_eventos()
    # contaminacion_a_cluster()
    # clusterizar_gran_evento()
    tiempo_a_cluster()


if __name__ == '__main__':
    main()