#! /usr/bin/env python

api='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0YWNvbmkyM0Bob3RtYWlsLmNvbSIsImp0aSI6ImJjNjYyMmU0LWI2NDAtNDMxMy1iMWFlLWNlNmRmODMwMzBmNyIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNTcwNzI1ODIzLCJ1c2VySWQiOiJiYzY2MjJlNC1iNjQwLTQzMTMtYjFhZS1jZTZkZjgzMDMwZjciLCJyb2xlIjoiIn0.XdD5zlXwGtJDZrD0nFmz3mqJ3rc4lGCnz_EItNpUIf0'
import requests
from datetime import datetime
# from influxdb import InfluxDBClient
from time import sleep, strftime
import csv, os
import json
import time
import pandas as pd

class aemet(object):

    def __init__(self, api):

        self.querystring = {"api_key": api}
        self.headers = {
            'cache-control': "no-cache"
        }

        self.file = 'datos.csv'
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass


    def get_idema(self):
        """

        :return: devuelve un dataframe con todas las estaciones
        """
        url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"
        response = requests.request("GET", url, headers=self.headers, params=self.querystring)
        dict = response.content
        dict = json.loads(dict.decode('utf-8'))
        url_datos = dict["datos"]
        datos = requests.get(url_datos).json()
        df = pd.read_json(json.dumps(datos), orient='list')
        return df

    def filter_provincia_idema(self, provincia):
        """

        :return: devuelve un dataframe con las estaciones correspondientes a la provincia indicada
        """
        df = self.get_idema()
        return df[df['provincia']==provincia]

    def get_datos_estacion(self, idema):
        """

        :param idema: Indentificador de la estación
        :return: devuelve un diccionario con los datos de la estación
        """
        url = 'https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/' + idema
        response = requests.request("GET", url, headers=self.headers, params=self.querystring).json()
        url_datos = response['datos']
        datos = requests.get(url_datos).json()
        return datos

    def get_param_estacion(self, idema):
        """
        METADATOS:

        idema: Indicativo climatógico de la estación meteorológia automática
        lon: Longitud de la estación meteorológica (grados)
        lat: Latitud de la estación meteorológica (grados)
        alt: Altitud de la estación en metros
        ubi: Ubicación de la estación. Nombre de la estación
        pacutp: Precipitación acumulada, medida por el disdrómetro, durante los 60 minutos anteriores a la hora indicada por el período de observación 'fint' (mm, equivalente a l/m2)
        pliqtp: Precipitación líquida acumulada durante los 60 minutos anteriores a la hora indicada por el período de observación 'fint' (mm, equivalente a l/m2)
        psolt: Precipitación sólida acumulada durante los 60 minutos anteriores a la hora indicada por el período de observación 'fint' (mm, equivalente a l/m2)
        vmax: Velocidad máxima del viento, valor máximo del viento mantenido 3 segundos y registrado en los 60 minutos anteriores a la hora indicada por el período de observación 'fint' (m/s)
        vv: Velocidad media del viento, media escalar de las muestras adquiridas cada 0,25 ó 1 segundo en el período de 10 minutos anterior al indicado por 'fint' (m/s)
        vmaxu: Velocidad máxima del viento (sensor ultrasónico), valor máximo del viento mantenido 3 segundos y registrado en los 60 minutos anteriores a la hora indicada por el período de observación 'fint' (m/s)
        vvu: Velocidad media del viento (sensor ultrasónico), media escalar en el periódo de 10 minutos anterior al indicado por 'fint' de las muestras adquiridas cada 0,25 ó 1 segundo (m/s)
        dv: Dirección media del viento, en el período de 10 minutos anteriores a la fecha indicada por 'fint' (grados)
        dvu: Dirección media del viento (sensor ultrasónico), en el período de 10 minutos anteriores a la fecha indicada por 'fint' (grados)
        dmax: Dirección del viento máximo registrado en los 60 minutos anteriores a la hora indicada por 'fint' (grados)
        dmaxu: Dirección del viento máximo registrado en los 60 minutos anteriores a la hora indicada por 'fint' por el sensor ultrasónico (grados)
        stdvv: Desviación estándar de las muestras adquiridas de velocidad del viento durante los 10 minutos anteriores a la fecha dada por 'fint' (m/s)
        stddv: Desviación estándar de las muestras adquiridas de la dirección del viento durante los 10 minutos anteriores a la fecha dada por 'fint' (grados)
        stdvvu: Desviación estándar de las muestras adquiridas de velocidad del viento durante los 10 minutos anteriores a la fecha dada por 'fint' obtenido del sensor ultrasónico de viento instalado junto al convencional (m/s)"
        stddvu: Desviación estándar de las muestras adquiridas de la dirección del viento durante los 10 minutos anteriores a la fecha dada por 'fint' obtenido del sensor ultrasónico de viento instalado junto al convencional (grados)
        hr: Humedad relativa instantánea del aire correspondiente a la fecha dada por 'fint' (%)
        inso: Duración de la insolación durante los 60 minutos anteriores a la hora indicada por el período de observación 'fint' (horas)
        pres: Presión instantánea al nivel en el que se encuentra instalado el barómetro y correspondiente a la fecha dada por 'fint' (hPa)
        pres_nmar: Valor de la presión reducido al nivel del mar para aquellas estaciones cuya altitud es igual o menor a 750 metros y correspondiente a la fecha indicada por 'fint' (hPa)
        ts: Temperatura suelo, temperatura instantánea junto al suelo y correspondiente a los 10 minutos anteriores a la fecha dada por 'fint' (grados Celsius)
        tss20cm: Temperatura subsuelo 20 cm, temperatura del subsuelo a una profundidad de 20 cm y correspondiente a los 10 minutos anteriores a la fecha dada por 'fint' (grados Celsius)
        tss5cm: Temperatura subsuelo 5 cm, temperatura del subsuelo a una profundidad de 5 cm y correspondiente a los 10 minutos anteriores a la fecha dada por 'fint' (grados Celsius)
        ta: Temperatura instantánea del aire correspondiente a la fecha dada por 'fint' (grados Celsius)
        tpr: Temperatura del punto de rocío calculado correspondiente a la fecha 'fint' (grados Celsius)
        tamin: Temperatura mínima del aire, valor mínimo de los 60 valores instantáneos de 'ta' medidos en el período de 60 minutos anteriores a la hora indicada por el período de observación 'fint' (grados Celsius)
        tamax: Temperatura máxima del aire, valor máximo de los 60 valores instantáneos de 'ta' medidos en el período de 60 minutos anteriores a la hora indicada por el período de observación 'fint' (grados Celsius)
        vis: Visibilidad, promedio de la medida de la visibilidad correspondiente a los 10 minutos anteriores a la fecha dada por 'fint' (Km)
        geo700: Altura del nivel de la superficie de referencia barométrica de 700 hPa calculado para las estaciones con altitud mayor de 2300 metros y correspondiente a la fecha indicada por 'fint' (m geopotenciales)
        geo850: Altura del nivel de la superficie de referencia barométrica de 850 hPa calculado para las estaciones con altitud mayor de 1000 metros y menor o igual a 2300 metros y correspondiente a la fecha indicada por 'fint' (m geopotenciales)
        geo925: Altura del nivel de la superficie barométrica de 925 hPa calculado para las estaciones con altitud mayor de 750 metros y y menor o igual a 1000 metros correspondiente a la fecha indicada por 'fint' (m geopotenciales)
        rviento: Recorrido del viento durante los 60 minutos anteriores a la fecha indicada por 'fint' (Hm)
        nieve: Espesor de la capa de nieve medid en los 10 minutos anteriores a la a la fecha indicada por 'fint' (cm)

        :param idema: Indentificador de la estación
        :return: devuelve la precipitación acumulada, medidad por el pluviometro, durante los 60 min anteriores a la hora indicada
        por el periodo de observación 'fint' (mm, equivalente a l/m2)
        """
        datos = self.get_datos_estacion(idema)
        inicio_medida = datos[-2].get('fint')
        fin_medida = datos[-1].get('fint')
        idema = datos[-1].get('idema')
        lon = datos[-1].get('lon')
        lat = datos[-1].get('lat')
        alt = datos[-1].get('alt')
        ubi = datos[-1].get('ubi')
        pacutp = datos[-1].get('pacutp')
        pliqtp = datos[-1].get('pliqtp')
        psolt = datos[-1].get('psolt')
        vmax = datos[-1].get('vmax')
        vv = datos[-1].get('vv')
        vmaxu = datos[-1].get('vmaxu')
        vvu = datos[-1].get('vvu')
        dv = datos[-1].get('dv')
        dvu = datos[-1].get('dvu')
        dmax = datos[-1].get('dmax')
        dmaxu = datos[-1].get('dmaxu')
        stdvv = datos[-1].get('stdvv')
        stddv = datos[-1].get('stddv')
        stdvvu = datos[-1].get('stdvvu')
        stddvu = datos[-1].get('stdduv')
        hr = datos[-1].get('hr')
        inso = datos[-1].get('inso')
        pres = datos[-1].get('pres')
        pres_mar = datos[-1].get('pres_mar')
        ts = datos[-1].get('ts')
        tss20cm = datos[-1].get('tss20cm')
        tss5cm = datos[-1].get('tss5cm')
        ta = datos[-1].get('ta')
        tpr = datos[-1].get('tpr')
        tamin = datos[-1].get('tamin')
        tamax = datos[-1].get('tamax')
        vis = datos[-1].get('vis')
        geo700 = datos[-1].get('geo700')
        geo850 = datos[-1].get('geo850')
        geo925 = datos[-1].get('geo925')
        rviento = datos[-1].get('rviento')
        nieve = datos[-1].get('nieve')
        prec = datos[-1].get('prec')

        dict={'inicio': inicio_medida, 'fin': fin_medida, 'prec': prec, 'idema': idema, 'lon': lon, 'lat': lat,
              'alt': alt, 'ubi': ubi, 'pacutp': pacutp, 'pliqtp': pliqtp, 'psolt': psolt, 'vmax': vmax, 'vv': vv,
              'vmaxu': vmaxu, 'vvu': vvu, 'dv': dv, 'dvu': dvu, 'dmax': dmax, 'dmaxu': dmaxu, 'stdvv': stdvv,
              'stddv': stddv, 'stdvvu': stdvvu, 'stddvu': stddvu, 'hr': hr, 'inso': inso, 'pres': pres, 'ts': ts,
              'pres_mar': pres_mar, 'tss20cm': tss20cm, 'tss5cm': tss5cm, 'ta': ta, 'tpr': tpr, 'tamin': tamin,
              'tamax': tamax, 'vis': vis, 'geo700': geo700, 'geo850': geo850, 'geo925': geo925, 'rviento': rviento,
              'nieve': nieve}

        list = []
        for k, v in dict.items():
            list.append(k)

        return dict

    #cabecera = ['idema', 'inicio', 'fin', 'lon', 'lat', 'prec', 'alt', 'ubi', 'pacutp', 'pliqtp', ]

    def get_datos_prec(self, estaciones):

        try:
            f = open(self.file, 'r+')
            flag = 0
        except:
            f = open(self.file, 'a+')
            flag = 1
        print(f.read())

        wr = csv.writer(f)
        data_csv = []
        for indice, fila in estaciones.iterrows():
            indicativo = fila['indicativo']
            try:
                dict = self.get_param_estacion(indicativo)
                for k, value in dict.items():
                    data_csv.append(value)
                wr.writerow(data_csv)
                data_csv = []

            except:
                print("no existe")
        if flag == 1:
            cabecera = []
            for k, value in dict.items():
                cabecera.append(k)

            print("añado cabecera")
        else:
            print("paso")

        f.close()

    def get_datos_est(self, estaciones):

        try:
            open(self.file, 'r')
            flag = 0
        except:
            flag = 1


        with open(self.file, 'a') as csvfile:
            fielnames = ['inicio', 'fin', 'prec', 'idema', 'lon', 'lat', 'alt', 'ubi', 'pacutp', 'pliqtp', 'psolt',
                         'vmax', 'vv', 'vmaxu', 'vvu', 'dv', 'dvu', 'dmax', 'dmaxu', 'stdvv', 'stddv', 'stdvvu',
                         'stddvu', 'hr', 'inso', 'pres', 'ts', 'pres_mar', 'tss20cm', 'tss5cm', 'ta', 'tpr', 'tamin',
                         'tamax', 'vis', 'geo700', 'geo850', 'geo925', 'rviento', 'nieve']
            wr = csv.DictWriter(csvfile, fieldnames=fielnames)
            if flag == 1:
                wr.writeheader()

            for indice, fila in estaciones.iterrows():
                indicativo = fila['indicativo']
                try:
                    dict = self.get_param_estacion(indicativo)
                    wr.writerow(dict)
                except:
                    print("no existe")

            csvfile.close()

estaciones = aemet(api=api)

estaciones_madrid = estaciones.filter_provincia_idema('MADRID')

while True:
    estaciones.get_datos_est(estaciones_madrid)
    print("dumiendo")
    sleep(3600)

