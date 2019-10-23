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

modelo = load_model("kmeans.21.3.joblib")

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

        sql = f'UPDATE AuxCamaras SET cluster = {cluster} WHERE id_camara = {id}'

        cur.execute(sql)

        connection.commit()

        print(id, cluster, cur.rowcount, "records affected")