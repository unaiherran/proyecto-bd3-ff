#! /usr/bin/env python
# -*- coding: utf-8 -*-

api='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0YWNvbmkyM0Bob3RtYWlsLmNvbSIsImp0aSI6ImJjNjYyMmU0LWI2NDAtNDMxMy1iMWFlLWNlNmRmODMwMzBmNyIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNTcwNzI1ODIzLCJ1c2VySWQiOiJiYzY2MjJlNC1iNjQwLTQzMTMtYjFhZS1jZTZkZjgzMDMwZjciLCJyb2xlIjoiIn0.XdD5zlXwGtJDZrD0nFmz3mqJ3rc4lGCnz_EItNpUIf0'
import requests
from datetime import datetime
# from influxdb import InfluxDBClient
from time import sleep, strftime
import csv, os
import json
import time
import pandas as pd

from io import StringIO
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DECIMAL, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
Base = declarative_base()
import os
import warnings
from sqlalchemy.exc import SAWarning


class aemet(object):

    def __init__(self, api):

        self.querystring = {"api_key": api}
        self.headers = {
            'cache-control': "no-cache"
        }

        self.base = 'proyecto'

        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass

    def make_date(self, str_fecha):
        """
            Metodo para convertir un string a datatime
        """
        formato_fecha = "%Y-%m-%dT%H:%M:%S"
        date = datetime.strptime(str_fecha, formato_fecha)
        return date

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

    def save_estaciones(self, df):
        db = BaseOne(self.base)
        session = db.sesion_inicio()

        for index, row in df.iterrows():
            codigo_estacion = row.get('indicativo')
            try:
                parametros = self.get_param_estacion(codigo_estacion)
                longitud = parametros.get('lon')
                latitud = parametros.get('lat')
                ubicacion = parametros.get('ubi')
                try:
                    # Compruebo que si existe el codigo de la estacion en la base
                    query = session.query(EstacionTiempo).get(
                        session.query(EstacionTiempo).filter(
                            EstacionTiempo.codigo_estacion == codigo_estacion).one().id)

                except:
                    estacion = EstacionTiempo(codigo_estacion=codigo_estacion, longitud=longitud, latitud=latitud,
                                              ubicacion=ubicacion)
                    session.add(estacion)
            except:
                pass

        session.commit()
        session.close()

    def save_datos(self, df):
        db = BaseOne(self.base)
        session = db.sesion_inicio()
        for index, row in df.iterrows():

            codigo_estacion = row.get('indicativo')
            print(codigo_estacion)
            try:
                print('entro')
                parametros = self.get_param_estacion(codigo_estacion)
                fecha_str = parametros.get('fin')
                fecha = self.make_date(fecha_str)
                pacutp = parametros.get('pacutp')
                pliqtp = parametros.get('pliqtp')
                psolt = parametros.get('psolt')
                vmax = parametros.get('vmax')
                vv = parametros.get('vv')
                vmaxu = parametros.get('vmaxu')
                vvu = parametros.get('vvu')
                dv = parametros.get('dv')
                dvu = parametros.get('dvu')
                dmax = parametros.get('dmax')
                dmaxu = parametros.get('dmaxu')
                stdvv = parametros.get('stdvv')
                stddv = parametros.get('stddv')
                stdvvu = parametros.get('stdvvu')
                stddvu = parametros.get('stddvu')
                hr = parametros.get('hr')
                inso = parametros.get('inso')
                pres = parametros.get('pres')
                pres_mar = parametros.get('pres_mar')
                ts = parametros.get('ts')
                tss20cm = parametros.get('tss20cm')
                tss5cm = parametros.get('tss5cm')
                ta = parametros.get('ta')
                tpr = parametros.get('tpr')
                tamin = parametros.get('tamin')
                tamax = parametros.get('tamax')
                vis = parametros.get('vis')
                rviento = parametros.get('rviento')
                nieve = parametros.get('nieve')
                prec = parametros.get('prec')

                estacion_id = session.query(EstacionTiempo).get(session.query(EstacionTiempo).filter(EstacionTiempo.codigo_estacion == codigo_estacion).one().id)
                query_estacion= session.query(EstacionTiempo).get(session.query(EstacionTiempo).filter(
                    EstacionTiempo.codigo_estacion == codigo_estacion).one().id)

                try:
                    # Compruebo que no exista la medida
                    query = session.query(MedidaTiempo).get(session.query(MedidaTiempo).filter(
                        MedidaTiempo.id == estacion_id.id, MedidaTiempo.fecha==fecha).one().id)

                except:

                    datos = MedidaTiempo(fecha=fecha, pacutp=pacutp, pliqtp=pliqtp, psolt=psolt, vmax=vmax, vv=vv,
                                         vmaxu=vmaxu, vvu=vvu, dv=dv, dvu=dvu, dmax=dmax, dmaxu=dmaxu, stdvv=stdvv,
                                         stddv=stddv, stdvvu=stdvvu, stddvu=stddvu, hr=hr, inso=inso, pres=pres,
                                         pres_mar=pres_mar, ts=ts, tss20cm=tss20cm, tss5cm=tss5cm, ta=ta, tpr=tpr,
                                         tamin=tamin, tamax=tamax, vis=vis, rviento=rviento, nieve=nieve, prec=prec)
                    query_estacion.MedidaTiempo.append(datos)
                    
            except:
                pass

        session.commit()
        session.close()
   
# Base de datos

class BaseOne(object):
    def __init__(self, nombre_base):

        # # Esta sera la base de datos general con las configuraciones
        uri = 'mysql+pymysql://admin:admmin00$$23@database-1.cluster-csy1i72nclox.eu-west-1.rds.amazonaws.com/' + nombre_base
        self.motor = create_engine(uri)
        Base.metadata.create_all(self.motor)
        self.Sesion = sessionmaker(bind=self.motor)
        self.Sesion.configure(bind=self.motor)

    def sesion_inicio(self):
        return self.Sesion()
 
class EstacionTiempo(Base):
    __tablename__='EstacionTiempo'
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, onupdate=datetime.now)
    codigo_estacion = Column(String(10))
    longitud = Column(DECIMAL(11, 8))
    latitud = Column(DECIMAL(10, 8))
    ubicacion = Column(String(100))

    MedidaTiempo = relationship('MedidaTiempo', back_populates='Estacion_Medida', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<EstacionTiempo(codigo_estacion = '%s')>" %(self.codigo_estacion)

class MedidaTiempo(Base):
    __tablename__='MedidaTiempo'
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, onupdate=datetime.now)
    fecha = Column(DateTime)
    pacutp = Column(Float)
    pliqtp = Column(Float)
    psolt = Column(Float)
    vmax = Column(Float)
    vv = Column(Float)
    vmaxu = Column(Float)
    vvu = Column(Float)
    dv = Column(Float)
    dvu = Column(Float)
    dmax = Column(Float)
    dmaxu = Column(Float)
    stdvv = Column(Float)
    stddv = Column(Float)
    stdvvu = Column(Float)
    stddvu = Column(Float)
    hr = Column(Float)
    inso = Column(Float)
    pres = Column(Float)
    pres_mar = Column(Float)
    ts = Column(Float)
    tss20cm = Column(Float)
    tss5cm = Column(Float)
    ta = Column(Float)
    tpr = Column(Float)
    tamin = Column(Float)
    tamax = Column(Float)
    vis = Column(Float)
    rviento = Column(Float)
    nieve = Column(Float)
    prec = Column(Float)

    Estacion_Medida = relationship('EstacionTiempo', back_populates='MedidaTiempo')
    estacion_id = Column(Integer, ForeignKey('EstacionTiempo.id'))

    def __repr__(self):
        return "<MedidaTiempo(fecha= %s)" %(self.fecha)

estaciones = aemet(api=api)
estaciones_madrid = estaciones.filter_provincia_idema('MADRID')
estaciones.save_estaciones(estaciones_madrid)

while True:
    # Guardo las medidas
    estaciones.save_datos(estaciones_madrid)
    # duerme durante una hora
    sleep(3600)


