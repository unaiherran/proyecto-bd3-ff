from datetime import datetime
from datetime import timedelta

import mysql.connector
from sqlalchemy import create_engine

import pandas as pd

from secret import *


DEBUG = True
LOCAL = False

outliers = 0.02

#dataframe auxiliar que guarda las ultimas medidas de trafico validas

cluster = list(range(200))
zeros = [0] * 200

last_good_traffic_reads = pd.DataFrame(list(zip(cluster, zeros, zeros, zeros, zeros,    # INT
                                                zeros, zeros, zeros, zeros,             # OCU
                                                zeros, zeros, zeros, zeros,             # CAR
                                                zeros, zeros, zeros, zeros,             # INT WOO
                                                zeros, zeros, zeros, zeros,             # OCU WOO
                                                zeros, zeros, zeros, zeros,             # CAR WOO
                                                zeros, zeros, zeros)),                  # OCU_MEAN(25,50,75)
                                       columns=['cluster', 'int_min', 'int_max', 'int_mean', 'int_median',
                                                'ocu_min', 'ocu_max', 'ocu_mean', 'ocu_median',
                                                'car_min', 'car_max', 'car_mean', 'car_median',
                                                'int_min_woo', 'int_max_woo', 'int_mean_woo', 'int_median_woo',
                                                'ocu_min_woo', 'ocu_max_woo', 'ocu_mean_woo', 'ocu_median_woo',
                                                'car_min_woo', 'car_max_woo', 'car_mean_woo', 'car_median_woo',
                                                'ocu_mean_25', 'ocu_mean_50', 'ocu_mean_75'])



# Conectarse a la base de datos
if not LOCAL:
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_database,
        port=db_port
    )


    engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_database}',
                           echo=False)

def dataframe_vacio_de_cluster():
    cluster = list(range(200))
    empty_df = pd.DataFrame(list(zip(cluster)),
                            columns=['cluster'])
    return empty_df


def calcular_de_imagenes_camara(fecha):

    sig_fecha = fecha + timedelta(minutes=15)

    empty_df = dataframe_vacio_de_cluster()

    # preparar respuesta si no funciona la consulta
    cluster = list(range(200))
    lst0 = [0] * 200
    lst_unknowns = [0] * 200
    df3 = pd.DataFrame(list(zip(cluster, lst_unknowns, lst_unknowns, lst_unknowns, lst_unknowns, lst_unknowns,
                                lst_unknowns, lst_unknowns, lst_unknowns)),
                       columns=['cluster', 'num_cars_min', 'num_cars_max', 'num_cars_mean', 'num_cars_median',
                                'num_cars_min_woo', 'num_cars_max_woo', 'num_cars_mean_woo',
                                'num_cars_median_woo'
                                ])

    format = '%Y-%m-%d %H:%M'

    fecha_str =  fecha.strftime(format)
    sig_fecha_str = sig_fecha.strftime(format)

    if not LOCAL:

        if connection.is_connected():

            sql = f"SELECT num_cars, cam.id_camara, ima.fecha, cam.cluster from ImagenesCamarasTrafico ima " \
                  f"INNER JOIN CamarasTrafico cam ON ima.id_camara = cam.id_camara where " \
                  f"(ima.fecha BETWEEN str_to_date('{fecha_str}', '%Y-%m-%d %H:%i') " \
                  f"AND str_to_date('{sig_fecha_str}', '%Y-%m-%d %H:%i'));"

            df = pd.read_sql(sql, con=connection)

            if not df.empty:
                df = df.sort_values(by=['cluster'])
                df_grouped = df.groupby('cluster').num_cars.agg(['min', 'max', 'mean', 'median'])
                df_grouped.columns = ['num_cars_min', 'num_cars_max', 'num_cars_mean', 'num_cars_median']
                df_grouped['cluster'] = list(df_grouped.index.values)
                df_grouped = df_grouped.rename_axis(None)

                # En df2 quitamos los outliers de las medidas
                df2 = df[df.groupby("cluster").num_cars.transform(
                    lambda x: (x < x.quantile(1-outliers)) & (x > (x.quantile(outliers)))).eq(1)]
                df2_grouped = df2.groupby('cluster').num_cars.agg(['min', 'max', 'mean', 'median'])
                df2_grouped.columns = ['num_cars_min_woo', 'num_cars_max_woo', 'num_cars_mean_woo',
                                       'num_cars_median_woo']
                df2_grouped['cluster'] = list(df2_grouped.index.values)
                df2_grouped = df2_grouped.rename_axis(None)

                # juntamos los dos dataframes
                df3 = pd.merge(empty_df, df_grouped, on='cluster', how='outer')
                df3 = pd.merge(df3, df2_grouped, on='cluster', how='outer')

                #quitamos las filas que tienen NaN en num_cars_mean
                df3 = df3.dropna(subset=['num_cars_mean'])

                # convertimos los NaN en 0 (los 999999 hace que el rmse se vaya a parla)
                df3 = df3.fillna(0)

    return df3


def calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high):
    # variable -> que queremos calcular. Tiene que ser "ocupacion", "intensidad" o "carga"
    # medidas -> lista con lo que se quiere medir ['mean', 'max', 'mean', 'median']
    # etiqueta -> lista con las etiquetas de las columnas

    quitar = ['ocupacion', 'intensidad', 'carga', 'error']
    quitar.remove(variable)

    df_quitando_outliers = df.drop(quitar, axis=1)

    # Calculo de la variable para valores de quitando los valores fuera de low & high
    res = df.groupby("cluster")[variable].quantile([low, high]).unstack(level=1)

    df_quitando_outliers = df_quitando_outliers.loc[((res.loc[df.cluster, low] <= df[variable].values) &
                                                     (df[variable].values <= res.loc[df.cluster, high])).values]

    df_respuesta = df_quitando_outliers.groupby('cluster')[variable].agg(medidas)

    df_respuesta.columns = etiqueta
    df_respuesta['cluster'] = list(df_respuesta.index.values)
    df_respuesta = df_respuesta.rename_axis(None)

    return df_respuesta


def fill_with_last_good_read(df):
    global last_good_traffic_reads

    # para cada columna
    columns = df.columns

    for col in columns:
        df[col] = df[col].fillna(last_good_traffic_reads[col])

    last_good_traffic_reads = df.copy()

    return df


def calcular_de_datos_trafico(fecha):

    empty_df = dataframe_vacio_de_cluster()

    # preparar respuesta si no funciona la consulta

    cluster = list(range(200))
    lst0 = [0] * 200
    df3 = pd.DataFrame(list(zip(cluster, lst0, lst0, lst0, lst0, lst0, lst0, lst0, lst0,lst0, lst0, lst0, lst0,
                                lst0, lst0, lst0,lst0, lst0, lst0, lst0,lst0, lst0, lst0, lst0,lst0, lst0, lst0, lst0)),
                       columns=['cluster', 'int_min', 'int_max', 'int_mean', 'int_median',
                                'ocu_min', 'ocu_max', 'ocu_mean', 'ocu_median',
                                'car_min', 'car_max', 'car_mean', 'car_median',
                                'int_min_woo', 'int_max_woo', 'int_mean_woo', 'int_median_woo',
                                'ocu_min_woo', 'ocu_max_woo', 'ocu_mean_woo', 'ocu_median_woo',
                                'car_min_woo', 'car_max_woo', 'car_mean_woo', 'car_median_woo',
                                'ocu_mean_25', 'ocu_mean_50', 'ocu_mean_75'])

    sig_fecha = fecha + timedelta(minutes=15)

    format = '%Y-%m-%d %H:%M'

    fecha_str = fecha.strftime(format)
    sig_fecha_str = sig_fecha.strftime(format)

    if not LOCAL:
        if connection.is_connected():
            sql = f"SELECT tra.intensidad, tra.ocupacion, tra.carga, tra.error, sen.cluster " \
                  f"from DatosTrafico tra INNER JOIN SensoresTrafico sen ON tra.id_sensor = sen.id " \
                  f"where (tra.fecha BETWEEN " \
                  f"str_to_date('{fecha_str}', '%Y-%m-%d %H:%i') AND " \
                  f"str_to_date('{sig_fecha_str}','%Y-%m-%d %H:%i')) AND " \
                  f"tra.error = 'N';"

            df = pd.read_sql(sql, con=connection)
            connection.commit()

            # Quitamos medidas incorrectas
            # Todas las negativas han de ser incorrectas por deficinicon
            # Además, tanto carga como intensidad son valores de 0 a 100

            index_names = df[(df['intensidad'] < 0)].index

            df.drop(index_names, inplace=True)

            index_names = df[(df['ocupacion'] < 0) | (df['ocupacion'] >= 100)].index
            df.drop(index_names, inplace=True)

            index_names = df[(df['carga'] < 0) | (df['carga'] >= 100)].index
            df.drop(index_names, inplace=True)

            df = df.dropna(how='any', axis=0)

            # Agrupamos y sacamos medias

            if not df.empty:
                df_grouped_int = df.groupby('cluster').intensidad.agg(['min', 'max', 'mean', 'median'])
                df_grouped_int.columns = ['int_min', 'int_max', 'int_mean', 'int_median']
                df_grouped_int['cluster'] = list(df_grouped_int.index.values)
                df_grouped_int = df_grouped_int.rename_axis(None)

                df_grouped_ocu = df.groupby('cluster').ocupacion.agg(['min', 'max', 'mean', 'median'])
                df_grouped_ocu.columns = ['ocu_min', 'ocu_max', 'ocu_mean', 'ocu_median']
                df_grouped_ocu['cluster'] = list(df_grouped_ocu.index.values)
                df_grouped_ocu = df_grouped_ocu.rename_axis(None)

                df_grouped_car = df.groupby('cluster').carga.agg(['min', 'max', 'mean', 'median'])
                df_grouped_car.columns = ['car_min', 'car_max', 'car_mean', 'car_median']
                df_grouped_car['cluster'] = list(df_grouped_car.index.values)
                df_grouped_car = df_grouped_car.rename_axis(None)

                # Calculo de la ocupacion para valores de + del 25% de la normal
                variable = 'ocupacion'
                medidas = ['mean']
                etiqueta = ['ocu_mean_25']
                low = 0.25
                high = 1.

                df_ocu_mean_25 = calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high)

                # Calculo de la ocupacion para valores de + del 50% de la normal
                etiqueta = ['ocu_mean_50']
                low = 0.5
                high = 1.

                df_ocu_mean_50 = calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high)

                # Calculo de la ocupacion para valores de + del 75% de la normal
                etiqueta = ['ocu_mean_75']
                low = 0.75
                high = 1.

                df_ocu_mean_75 = calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high)

                # Calculo de la intensidad para valores quitando outliers
                variable = 'intensidad'
                etiqueta = ['int_min_woo', 'int_max_woo', 'int_mean_woo', 'int_median_woo']

                medidas = ['min', 'max', 'mean', 'median']
                low = 0.05
                high = 0.95

                df_grouped_int_woo = calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high)


                # Calculo de la carga para valores quitando outliers
                variable = 'carga'
                etiqueta = ['car_min_woo', 'car_max_woo', 'car_mean_woo', 'car_median_woo']

                medidas = ['min', 'max', 'mean', 'median']
                low = 0.05
                high = 0.95

                df_grouped_car_woo = calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high)


                # Calculo de la ocupacion para valores quitando outliers
                variable = 'ocupacion'
                etiqueta = ['ocu_min_woo', 'ocu_max_woo', 'ocu_mean_woo', 'ocu_median_woo']

                medidas = ['min', 'max', 'mean', 'median']
                low = 0.05
                high = 0.95

                df_grouped_ocu_woo = calculo_de_variable_quitando_outliers(df, variable, medidas, etiqueta, low, high)

                df3 = pd.merge(empty_df, df_grouped_int, on='cluster', how='outer')
                df3 = pd.merge(df3, df_grouped_ocu, on='cluster', how='outer')
                df3 = pd.merge(df3, df_grouped_car, on='cluster', how='outer')
                df3 = pd.merge(df3, df_grouped_int_woo, on='cluster', how='outer')
                df3 = pd.merge(df3, df_grouped_ocu_woo, on='cluster', how='outer')
                df3 = pd.merge(df3, df_grouped_car_woo, on='cluster', how='outer')
                df3 = pd.merge(df3, df_ocu_mean_25, on='cluster', how='outer')
                df3 = pd.merge(df3, df_ocu_mean_50, on='cluster', how='outer')
                df3 = pd.merge(df3, df_ocu_mean_75, on='cluster', how='outer')

                # df3 = df3.dropna(subset=['int_mean', 'car_mean', 'ocu_mean'])

                df3 = fill_with_last_good_read(df3)

    return df3


def calcular_de_eventos(fecha):

    fecha_ini = fecha - timedelta(minutes=120)
    fecha_fin = fecha + timedelta(minutes=60)
    format = '%Y-%m-%d %H:%M'

    # preparar respuesta si no funciona la consulta
    cluster = list(range(200))
    lst0 = [0] * 200
    df3 = pd.DataFrame(list(zip(cluster, lst0, lst0, lst0, lst0, lst0, lst0)),
                       columns=['cluster', 'eve_3h', 'eve_3h_g', 'eve_2h', 'eve_2h_g', 'eve_1h', 'eve_1h_g'])

    fecha_ini_str = fecha_ini.strftime(format)
    fecha_fin_str = fecha_fin.strftime(format)

    if not LOCAL:
        if connection.is_connected():
            cur = connection.cursor();

            sql = f"SELECT fecha, gratuito, cluster from DatosEventos eve " \
                  f"where (eve.fecha BETWEEN " \
                  f"str_to_date('{fecha_ini_str}', '%Y-%m-%d %H:%i') AND " \
                  f"str_to_date('{fecha_fin_str}','%Y-%m-%d %H:%i'));"

            df = pd.read_sql(sql, con=connection)

            if not df.empty:
                df['evento'] = 1
                df['fecha'] = pd.to_datetime(df['fecha'])
                df = df.sort_values(by=['cluster'])

                # Eventos 3h (-120 -> +60)
                df3h = df.groupby('cluster').sum()

                df3h.columns = ['eve_3h_g', 'eve_3h']
                df3h['cluster'] = list(df3h.index.values)
                df3h.index.name = None

                # Eventos 2h (-60 -> +60)
                start_date = fecha - timedelta(minutes=60)
                end_date = fecha + timedelta(minutes=60)
                mask = (df['fecha'] > start_date) & (df['fecha'] <= end_date)
                df2 = df.loc[mask]
                df2h = df2.groupby('cluster').sum()
                df2h.columns = ['eve_2h_g', 'eve_2h']
                df2h['cluster'] = list(df2h.index.values)
                df2h.index.name = None

                # Eventos 1h (-30 -> +30)
                start_date = fecha - timedelta(minutes=30)
                end_date = fecha + timedelta(minutes=30)
                mask = (df['fecha'] > start_date) & (df['fecha'] <= end_date)
                df1 = df.loc[mask]
                df1h = df1.groupby('cluster').sum()
                df1h.columns = ['eve_1h_g', 'eve_1h']
                df1h['cluster'] = list(df1h.index.values)
                df1h.index.name = None

                # merge de todos los df
                df3 = dataframe_vacio_de_cluster()

                df3 = pd.merge(df3, df3h, on='cluster', how='outer')
                df3 = pd.merge(df3, df2h, on='cluster', how='outer')
                df3 = pd.merge(df3, df1h, on='cluster', how='outer')

                df3 = df3.fillna(0)
                df3 = df3.astype({"eve_3h": int, "eve_3h_g": int, "eve_2h": int,
                                  "eve_2h_g": int,"eve_1h": int, "eve_1h_g": int })

    return df3


def calcular_de_fecha(fecha):
    dia_semana = fecha.weekday()
    dia = fecha.day
    festivo = 0

    if not LOCAL:
        if connection.is_connected():
            cur = connection.cursor();

            sql = f"SELECT * FROM Festivos where fecha=str_to_date('{fecha.year}-{fecha.month}-{fecha.day}'" \
                  f", '%Y-%m-%d');"

            cur.execute(sql)

            data = cur.fetchall()

            if data:
                festivo = 1

    cluster = list(range(200))
    lst_dia_semana = [dia_semana] * 200
    lst_dia_mes = [dia] * 200
    lst_festivo = [festivo] * 200
    lst_fecha =[fecha] * 200

    df3 = pd.DataFrame(list(zip(cluster, lst_dia_semana, lst_dia_mes, lst_festivo, lst_fecha)),
                       columns=['cluster', 'dia_semana', 'dia_mes', 'festivo', 'fecha'])

    return df3


def calcular_de_tiempo(fecha):
    fecha_anterior = fecha - timedelta(hours=3)
    fecha_posterior = fecha + timedelta(minutes=15)

    if not LOCAL:
        if connection.is_connected():
            sql = f"SELECT tie.fecha, vmax, vv,dv,dmax, ta, tamin, tamax, prec, clu.id_cluster FROM " \
                  f"proyecto.MedidaTiempo2 tie inner join Cluster clu on clu.meteo = estacion_id " \
                  f"WHERE tie.fecha between '{fecha_anterior}' and '{fecha_posterior}' order by tie.fecha desc;"


            df = pd.read_sql(sql, con=connection)

            # las lecturas de tiempo se publican cada hora. Cuando generamos el training dataset bastaría con sacar
            # la lectura de esa hora, pero cuando estás haciendo predicciones en tiempo real, puede que los parametros
            # meteorologicos no esten aun disponibles, con lo que hacemos una query mas ancha y nos quedamos con el
            # valor más reciente
            try:
                fecha_mas_reciente = df.iloc[0]['fecha']
                filtro_fecha = df['fecha'] == fecha_mas_reciente
                df = df[filtro_fecha]
            except IndexError:
                print('Dataframe de tiempo vacio')

            df = df.drop(['fecha'], axis=1)

            df = df.dropna()
            # rename column id_cluster a cluster
            df = df.rename(columns={"id_cluster": "cluster"})

            if not df.empty:
                df3 = df
            else:
                # fill df with 0
                cluster = list(range(200))
                unknown = [0] * 200
                df['cluster'] = cluster
                df['vmax'] = unknown
                df['vv'] = unknown
                df['dv'] = unknown
                df['dmax'] = unknown
                df['ta'] = unknown
                df['tamin'] = unknown
                df['tamax'] = unknown
                df['prec'] = unknown
                df3 = df

    return df3


def calcular_de_gran_evento(fecha):
    cluster = list(range(200))
    lst0 = [0] * 200
    df3 = pd.DataFrame(list(zip(cluster, lst0)), columns=['cluster', 'gran_evento'])

    fecha_ini = fecha - timedelta(hours=12)
    fecha_fin = fecha + timedelta(hours=12)
    format = '%Y-%m-%d %H:%M'

    if not LOCAL:
        if connection.is_connected():
            sql = f"SELECT * FROM DatosGrandesEventos ge WHERE " \
                  f"(ge.fecha BETWEEN str_to_date('{fecha_ini.strftime(format)}', '%Y-%m-%d %H:%i') AND " \
                  f"str_to_date('{fecha_fin.strftime(format)}','%Y-%m-%d %H:%i'));"
            df = pd.read_sql(sql, con=connection)

            for _, row in df.iterrows():
                duracion = row['fechaFin'] - row['fecha']
                fecha_inicio = row['fecha'] - timedelta(minutes=90)
                fecha_final = row['fechaFin'] + timedelta(minutes=60)
                if fecha > fecha_inicio and fecha < fecha_final:
                    # el Evento afecta a el trafico en los clusters que esten en los alrededores
                    try:
                        clusters_afectados_lts_str = row['clusters_cercanos'].split(' ')
                        clusters_afectados_lts_str.append(row['cluster'])

                        for clu in clusters_afectados_lts_str:
                            if clu == '': continue
                            df3.iloc[int(clu)]['gran_evento'] += 1
                    except AttributeError:
                        print('Cliuster no tiene eventos')
    return df3


def insert_en_train_1_db(tb, df):
    if not LOCAL:
        if connection.is_connected():
            df.to_sql(name=tb, con=engine, if_exists='append', index=True)


def calculo_parametros_un_train(fecha, tb='train_1', save_in_db=True):
    # Fecha es datetime
    # Cluster es int
    empty_df = dataframe_vacio_de_cluster()

    # calculo de db_imagenes_camara

    if save_in_db:
        print(f'{datetime.now()} -> Realizando cálculos fecha:{fecha}')
        print(datetime.now(), 'Calculando imagenes     ',end='\r')
    # df_coches = calcular_de_imagenes_camara(fecha)

    # calculo de db_datos_trafico
    if save_in_db:
        print(datetime.now(), ' Calculando datos trafico ', end='\r')

    df_trafico = calcular_de_datos_trafico(fecha)

    #calculo de db_festivos
    if save_in_db:
        print(datetime.now(), 'Calculando festivos       ', end='\r')

    df_fecha = calcular_de_fecha(fecha)

    # calculo de db_eventos
    if save_in_db:
        print(datetime.now(), 'Calculando eventos        ', end='\r')
    df_eventos = calcular_de_eventos(fecha)

    # calculo de db_grandes_Eventos
    if save_in_db:
        print(datetime.now(), 'Calculando Grandes Eventos', end='\r')
    df_grandes_eventos = calcular_de_gran_evento(fecha)

    # calculo de db_contaminacion
    if save_in_db:
        print(datetime.now(), 'Calculando contaminacion  ', end='\r')
    # df_contaminacion = calcular_de_contaminacion(fecha)

    # calculo de db_tiempo
    if save_in_db:
        print(datetime.now(), 'Calculando tiempo         ', end='\r')

    df_tiempo = calcular_de_tiempo(fecha)

    # merge de todos los dataframes
    df = pd.merge(empty_df, df_trafico, on='cluster', how='outer')
    df = pd.merge(df, df_fecha, on='cluster', how='outer')
    df = pd.merge(df, df_eventos, on='cluster', how='outer')
    df = pd.merge(df, df_tiempo, on='cluster', how='outer')
    df = pd.merge(df, df_grandes_eventos, on='cluster', how='outer')

    # escribir en bdd train_1

    if save_in_db:
        print(datetime.now(), 'Escribiendo en dbb       \r', end='\r')
        insert_en_train_1_db(tb, df)
    else:
        return df


def bucle(fecha_ini, fecha_fin, tb, inc_minutes=15):
    fecha = fecha_ini
    while fecha <= fecha_fin:
        calculo_parametros_un_train(fecha, tb)

        fecha = fecha + timedelta(minutes=inc_minutes)


def main():
    # COge todos los datos desde el 20/10 hasta hoy
    # SI NO HAY DATOS DE COCHES NO GRABA NADA

    #Train Data
    tb = 'grouped_data_0'

    fecha_ini = datetime.strptime("20-10-2019 00:00", "%d-%m-%Y %H:%M")
    fecha_fin = datetime.strptime("25-11-2019 00:00", "%d-%m-%Y %H:%M")

    #Test Data
    # tb = 'test_data_0'
    # fecha_ini = datetime.strptime("18-11-2019 00:00", "%d-%m-%Y %H:%M")
    # fecha_fin = datetime.strptime("21-11-2019 21:59", "%d-%m-%Y %H:%M")

    bucle(fecha_ini, fecha_fin, tb)


if __name__ == '__main__':
    main()