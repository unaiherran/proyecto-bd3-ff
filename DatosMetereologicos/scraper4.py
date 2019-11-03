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



class aemet(object):

    def __init__(self, api):

        self.querystring = {"api_key": api}
        self.headers = {
            'cache-control': "no-cache"
        }

        self.file = 'datos.csv'
        self.base = 'proyecto'

        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass

    def make_date(self, str_fecha):
        formato_fecha = "%Y-%m-%dT%H:%M:%S"
        date = datetime.strptime(str_fecha, formato_fecha)
        return date

    def open_csv(self):
        fielnames = ['inicio', 'fin', 'prec', 'idema', 'lon', 'lat', 'alt', 'ubi', 'pacutp', 'pliqtp', 'psolt',
                     'vmax', 'vv', 'vmaxu', 'vvu', 'dv', 'dvu', 'dmax', 'dmaxu', 'stdvv', 'stddv', 'stdvvu',
                     'stddvu', 'hr', 'inso', 'pres', 'ts', 'pres_mar', 'tss20cm', 'tss5cm', 'ta', 'tpr', 'tamin',
                     'tamax', 'vis', 'geo700', 'geo850', 'geo925', 'rviento', 'nieve']
        df = pd.read_csv(self.file, sep=',', names=fielnames, skiprows=1)

        return df

    def carga_datos_csv(self, df):
        db = BaseOne(self.base)
        session = db.sesion_inicio()
        for index, row in df.iterrows():

            codigo_estacion = row.get('idema')
            try:
                fecha_str = row.get('fin')
                fecha = self.make_date(fecha_str)
                pacutp = float(row.get('pacutp'))
                pliqtp = float(row.get('pliqtp'))
                psolt = float(row.get('psolt'))
                vmax = float(row.get('vmax'))
                vv = float(row.get('vv'))
                vmaxu = float(row.get('vmaxu'))
                vvu = float(row.get('vvu'))
                dv = float(row.get('dv'))
                dvu = float(row.get('dvu'))
                dmax = float(row.get('dmax'))
                dmaxu = float(row.get('dmaxu'))
                stdvv = float(row.get('stdvv'))
                stddv = float(row.get('stddv'))
                stdvvu = float(row.get('stdvvu'))
                stddvu = float(row.get('stddvu'))
                hr = float(row.get('hr'))
                inso = float(row.get('inso'))
                pres = float(row.get('pres'))
                pres_mar = float(row.get('pres_mar'))
                ts = float(row.get('ts'))
                tss20cm = float(row.get('tss20cm'))
                tss5cm = float(row.get('tss5cm'))
                ta = float(row.get('ta'))
                tpr = float(row.get('tpr'))
                tamin = float(row.get('tamin'))
                tamax = float(row.get('tamax'))
                vis = float(row.get('vis'))
                rviento = float(row.get('rviento'))
                nieve = float(row.get('nieve'))
                prec = float(row.get('prec'))

                estacion_id = session.query(EstacionTiempo).get(session.query(EstacionTiempo).filter(
                    EstacionTiempo.codigo_estacion == codigo_estacion).one().id)

                try:

                    j = 0
                    for i in estacion_id.MedidaTiempo:
                         if i.fecha == fecha:
                             j= 1

                    if j == 0:
                        raise NameError('No existe la fecha')


                except Exception as error:
                #
                    print(error)
                #
                    datos = MedidaTiempo(fecha=fecha, pacutp=pacutp, pliqtp=pliqtp, psolt=psolt, vmax=vmax, vv=vv,
                                         vmaxu=vmaxu, vvu=vvu, dv=dv, dvu=dvu, dmax=dmax, dmaxu=dmaxu, stdvv=stdvv,
                                         stddv=stddv, stdvvu=stdvvu, stddvu=stddvu, hr=hr, inso=inso, pres=pres,
                                         pres_mar=pres_mar, ts=ts, tss20cm=tss20cm, tss5cm=tss5cm, ta=ta, tpr=tpr,
                                         tamin=tamin, tamax=tamax, vis=vis, rviento=rviento, nieve=nieve, prec=prec)
                    estacion_id.MedidaTiempo.append(datos)
                    print("guardo datos estacion: ", datos)

            except Exception as e:
                 print(str(e))


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

    def inspect(self):
        inspector = inspect(self.motor)
        for table_name in inspector.get_table_names():
            for column in inspector.get_columns(table_name):
                print("Column: %s" % column['name'])

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
    __tablename__='MedidaTiempo2'
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
file_csv = estaciones.open_csv()
estaciones.carga_datos_csv(file_csv)






