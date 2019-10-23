from decimal import Decimal
from datetime import datetime, date, timedelta

import mysql.connector
from secret import *

connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    passwd=db_passwd,
    database=db_database,
    port=db_port
)

if connection.is_connected():
    cur = connection.cursor()
    q = "SELECT * FROM AuxCamaras;"
    cur.execute(q)

    data = cur.fetchall()
    print(data)

    for d in data:
        id = d[0]
        longitud = d[2]
        latitud = d[3]
        print(id, longitud, latitud)

        cluster = 1

        sql = f'UPDATE AuxCamaras SET cluster = {cluster} WHERE id_camara = {id}'

        cur.execute(sql)

        connection.commit()

        print(cur.rowcount, "records affected")