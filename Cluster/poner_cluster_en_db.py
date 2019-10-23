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
        print(d)
