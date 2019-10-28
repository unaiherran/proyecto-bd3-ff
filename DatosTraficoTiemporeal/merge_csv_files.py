import glob
import logging
import math
import numbers
import os
import time

import mysql.connector
import pandas as pd

from config import *

logging.basicConfig(level=logging.INFO, filename='merger_realtime.log', filemode='a',
                    format='%(asctime)s - %(message)s')


def merge_data():
    logging.info('Merging realtime traffic data ...')
    os.chdir("csv")

    logging.info('Connecting to database ...')
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_database,
        port=db_port
    )

    if connection.is_connected():

        while True:
            logging.info('Searching csv files ...')
            extension = 'csv'
            all_filenames = [i for i in glob.glob('*.{}'.format(extension))][:10]
            logging.info(f'Found {len(all_filenames)} files')
            logging.info(f'Files {all_filenames}')

            if len(all_filenames) > 0:
                logging.info('Mergering ...')
                # combine all files in the list
                combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames], sort=False)

                logging.info('Processing ...')

                # invalid_date_df = combined_csv.ix[~combined_csv.fecha.str.contains('(\d{2})[/](\d{2})[/](\d{4})')]
                # invalid_date_df.head(100)
                combined_csv['fecha'] = pd.to_datetime(combined_csv['fecha'], format='%d/%m/%Y %H:%M:%S',
                                                       errors='coerce')
                combined_csv['dia_semana'] = combined_csv['fecha'].dt.dayofweek
                combined_csv['mes'] = combined_csv['fecha'].dt.month
                combined_csv['hora'] = combined_csv['fecha'].dt.hour.map(str)
                combined_csv['minutos'] = combined_csv['fecha'].dt.minute.apply(lambda x: '{0:0>2}'.format(x))

                logging.info('Writing ...')
                cursor = connection.cursor()

                for index, row in combined_csv.iterrows():
                    # print(row)

                    for k, v in row.items():
                        if isinstance(v, numbers.Number) and math.isnan(v):
                            row[k] = 0

                    if row.get("idelem") == 0 or row.get("idelem") >= 10495:
                        continue
                    row['dia_semana'] = str(row['dia_semana']).replace(".0", "")
                    row['mes'] = str(row['mes']).replace(".0", "")
                    row['hora'] = str(row['hora']).replace(".0", "")
                    row['minutos'] = str(row['minutos']).replace(".0", "")

                    sql = f'INSERT INTO DatosTrafico (id_sensor, fecha, intensidad, ocupacion, carga, nivelServicio, intensidadSat, \
error, subarea, st_x, st_y, dia_semana, mes, hora) VALUES({row.get("idelem")}, \'{row.get("fecha")}\', \
{row.get("intensidad")}, {row.get("ocupacion")}, {row.get("carga")}, {row.get("nivelServicio")}, \
{row.get("intensidadSat")}, \'{row.get("error")}\', {row.get("subarea")}, {row.get("st_x").replace(",", ".")}, {row.get("st_y").replace(",", ".")}, \
{row.get("dia_semana")}, {row.get("mes")}, {row.get("hora")}{row.get("minutos")});'
                    logging.debug(sql)
                    cursor.execute(sql)
                # close the connection to the database.
                cursor.close()

                logging.info('Done ...')

                for f in all_filenames:
                    os.rename(f, f"{f}.added")

                # combined_csv.to_csv("combined_traffic_realtime.csv", index=False, encoding='utf-8-sig')
                # engine = create_engine('mysql+mysqldb://[user]:[pass]@[host]:[port]/[schema]', echo=False)
                # combined_csv.to_sql(con=connection, name='DatosTrafico', if_exists='replace')
            connection.commit()
            logging.info('Waiting ...')
            time.sleep(60)


if __name__ == "__main__":
    merge_data()
