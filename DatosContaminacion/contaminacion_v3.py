#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pandas as pd
from io import StringIO
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DECIMAL, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from time import sleep
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
Base = declarative_base()
Base2 = declarative_base()
import os
import pymysql
import numpy as np

import warnings
from sqlalchemy.exc import SAWarning

warnings.filterwarnings('ignore',
 r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively\, "
 "and SQLAlchemy must convert from floating point - rounding errors and other "
 "issues may occur\. Please consider storing Decimal numbers as strings or "
 "integers on this platform for lossless storage\.$",
 SAWarning, r'^sqlalchemy\.sql\.type_api$')

class contaminacion(object):

    def __init__(self):
        self.url_txt = "https://datos.madrid.es/egob/catalogo/212531-7916318-calidad-aire-tiempo-real.txt"
        self.url_csv_contaminacion = 'https://datos.madrid.es/egob/catalogo/212531-10515086-calidad-aire-tiempo-real.csv'
        self.url_csv_estacioes = "https://datos.madrid.es/egob/catalogo/212629-1-estaciones-control-aire.csv"

    def get_txt(self):

        response = requests.get(self.url_txt, headers={"User-Agent": "curl/7.61.0"})
        data = StringIO(response.content.decode('utf-8'))
        names = ["PROVINCIA", "MUNICIPIO",	"ESTACION",	'MAGNITUD',"PUNTO", "MUESTREO", "ANO",	"MES",	"DIA",	"H01",
                 "V01",	"H02",	"V02",	"H03",	"V03",	"H04",	"V04",	"H05",	"V05",	"H06",	"V06",	"H07",	"V07",
                 "H08",	"V08",	"H09",	"V09",	"H10",	"V10",	"H11",	"V11",	"H12",	"V12",	"H13",	"V13",	"H14",
                 "V14",	"H15",	"V15",	"H16",	"V16",	"H17",	"V17",	"H18",	"V18",	"H19",	"V19",	"H20",	"V20",
                 "H21",	"V21",	"H22",	"V22",	"H23",	"V23",	"H24",	"V24"]

        df = pd.read_csv(data, sep=',', names=names)
        return df

    def get_csv_estaciones(self):
        response = requests.get(self.url_csv_estacioes, headers={"User-Agent": "curl/7.61.0"})
        data = StringIO(response.content.decode('iso-8859-1'))
        df = pd.read_csv(data, sep=';')
        return df

    def make_date(self, str_fecha):
        formato_fecha = "%d-%m-%Y %H:%M:%S"
        date = datetime.strptime(str_fecha, formato_fecha)
        return date + timedelta(hours=1)

    def save_magnitud(self):

        df = pd.DataFrame(columns=('codigo', 'descripcion', 'unidad'))

        codigos = [1, 6, 7, 8, 9, 10, 12, 14, 20, 30, 35, 37, 38, 39, 42, 43, 44]
 
        descripcion = ['Dióxido de Azufre', 'Monóxido de Carbono', 'Monóxido de Nitrógeno', 'Dióxido de Nitrógeno',
                       'Partículas < 2.5 um', 'Partículas < 10 um', 'Oxidos de Nitrógeno', 'Ozono', 'Tolueno',
                       'Benzeno',
                       'Etilbenceno', 'Metaxileno', 'Paraxileno', 'Ortoxileno', 'Hidrocarburos totales (hexano)',
                       'Metano', 'Hidrocarburos no metánicos (hexano)']

        unidad = ['ug/m3', 'mg/m3', 'ug/m3', 'ug/m3', 'ug/m3', 'ug/m3', 'ug/m3', 'ug/m3', 'ug/m3', 'ug/m3', 'ug/m3',
                  'ug/m3', 'ug/m3', 'ug/m3', 'mg/m3', 'mg/m3', 'mg/m3']

        df['codigo'] = codigos
        df['descripcion'] = descripcion
        df['unidad'] = unidad

        db = BaseOne('proyecto')
        session = db.sesion_inicio()

        query_estacion = session.query(DatoEstacion).all()

        for estacion in query_estacion:

            for index, row in df.iterrows():
                codigo = str(row['codigo'])
                descripcion = str(row['descripcion'])
                unidad = str(row['unidad'])
                estacion_id = estacion.id

                try:
                    query = session.query(TableMagnitud).get(session.query(TableMagnitud).
                                                             filter(TableMagnitud.codigo == codigo, TableMagnitud.estacion_id==estacion_id).one().id)

                except:
                    data = TableMagnitud(codigo=codigo, descripcion=descripcion, unidad=unidad)
                    estacion.table_magnitud.append(data)

        session.commit()
        session.close()

    def get_estacion(self, session, codigo):
        query = session.query(DatoEstacion).get(session.query(DatoEstacion).filter(DatoEstacion.codigo == codigo).one().id)
        return query

    def save_contaminacion(self):
        df = self.get_txt()

        cols_H = {'{:02d}'.format(i): ('H' + '{:02d}'.format(i + 1), 'V' + '{:02d}'.format(i+1) ) for i in range(0, 24)}

        db = BaseOne('proyecto')
        session = db.sesion_inicio()
        for index, value in df.iterrows():
            fila = df.iloc[index]
            provincia = str(fila['PROVINCIA'])
            municipio = '{:03d}'.format(int(fila['MUNICIPIO']))
            estacion = '{:03d}'.format(int(fila['ESTACION']))
            magnitud = str(fila['MAGNITUD'])
            codigo_estacion = provincia + municipio + estacion

            query_estacion = session.query(DatoEstacion).get(session.query(DatoEstacion).filter(DatoEstacion.codigo == codigo_estacion).one().id)
            estacion_id = query_estacion.id

            # Hay una magnitud, la 22 que está en prueaba
            try:
                query_magnitud = session.query(TableMagnitud).filter(TableMagnitud.estacion_id == estacion_id, TableMagnitud.codigo == magnitud).one()

                # fecha
                ano = str(fila['ANO'])
                mes = str(fila['MES'])
                dia = str(fila['DIA'])
                magnitud_id = query_magnitud.id

                for k, v in cols_H.items():
                    str_fecha = dia + '-' + mes + '-' + ano + ' ' + k + ':00:00'
                    fecha = self.make_date(str_fecha)
                    valor = fila[v[0]]
                    validez = fila[v[1]]
                    query = session.query(TableContaminacion).filter(TableContaminacion.fecha == fecha,
                                                                     TableContaminacion.magnitud_id == magnitud_id)
                    try:
                        test = session.query(TableContaminacion).get(query.one().id)
                        if validez != test.validez:
                            query.update({'valor': valor, 'validez': validez})
                            print("actualizado")

                    except:
                        dato = TableContaminacion(fecha=fecha, valor=valor, validez=validez)

                        query_magnitud.table_contaminacion.append(dato)

            except:
                pass

        session.commit()
        session.close()

    def save_estaciones(self):
        df = self.get_csv_estaciones()
        db = BaseOne('proyecto.db')
        session = db.sesion_inicio()
        for index, row in df.iterrows():
           # row es la fila
            codigo = row['CODIGO']
            codigo_corto = row['CODIGO_CORTO']
            estacion = row['ESTACION']
            direccion = row['DIRECCION']
            altitud = row['ALTITUD']
            cod_tipo = row['COD_TIPO']
            nom_tipo = row['NOM_TIPO']
            no2 = row['NO2']
            so2 = row['SO2']
            co = row['CO']
            pm10 = row['PM10']
            pm2_5 = row['PM2_5']
            o3 = row['O3']
            btx = row['BTX']
            hc = row['HC']
            cod_via = row['COD_VIA']
            via_clase = row['VIA_CLASE']
            via_par = row['VIA_PAR']
            via_nombre = row['VIA_NOMBRE']
            fecha_alta_str = row['Fecha alta']
            fecha_alta = datetime.strptime(fecha_alta_str, "%d/%m/%Y").date()
            longitud = row['LONGITUD']
            latitud = row['LATITUD']

            try:
                query = session.query(DatoEstacion).get(session.query(DatoEstacion).filter(DatoEstacion.codigo == codigo).one().id)
            except:
                data = DatoEstacion(codigo=codigo, codigo_corto=codigo_corto, estacion=estacion, direccion=direccion,
                                    altitud=altitud, cod_tipo=cod_tipo, nom_tipo=nom_tipo, no2=no2, so2=so2, co=co,
                                    pm10=pm10, pm2_5=pm2_5, o3=o3, btx=btx, hc=hc, cod_via=cod_via, via_clase=via_clase,
                                    via_par=via_par, via_nombre=via_nombre, fecha_alta=fecha_alta, longitud=longitud,
                                    latitud=latitud)
                session.add(data)

        session.commit()
        session.close()

    def print_table(self):
        db = BaseOne('proyecto')
        db.inspect()


# Tablas base de datos
class BaseOne(object):
    def __init__(self, nombre_base):

        # # Esta sera la base de datos general con las configuraciones
      #  self.motor = create_engine('sqlite:///./' + nombre_base)
        uri = 'mysql+pymysql://admin:admmin00$$23@database-1.cluster-csy1i72nclox.eu-west-1.rds.amazonaws.com/' + nombre_base
        self.motor = create_engine(uri)
       # uri = 'mysql+pymysql://admin:admmin00$$23@database-1.cluster-csy1i72nclox.eu-west-1.rds.amazonaws.com/' + nombre_base
       # ssl_args = {'ssl': {'key': 'ec2-proyecto-bd3-ff.pem'}}
       # self.motor = create_engine(uri, connect_args=ssl_args )
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



class DatoEstacion(Base):
    __tablename__='contaminacion_estacion'
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, onupdate=datetime.now)
    codigo = Column(Integer)
    codigo_corto = Column(Integer)
    estacion = Column(String(50))
    direccion = Column(String(100))
    altitud = Column(Integer)
    cod_tipo = Column(String(4))
    nom_tipo = Column(String(25))
    no2 = Column(String(1))
    so2 = Column(String(1))
    co = Column(String(1))
    pm10 = Column(String(1))
    pm2_5 = Column(String(1))
    o3 = Column(String(1))
    btx = Column(String(1))
    hc = Column(String(1))
    cod_via = Column(Integer)
    via_clase = Column(String(15))
    via_par = Column(String(5))
    via_nombre = Column(String(50))
    fecha_alta = Column(Date)
    longitud = Column(DECIMAL(11, 8))
    latitud = Column(DECIMAL(10, 8))
    table_magnitud = relationship('TableMagnitud', back_populates='estacion_magnitud',
                                   cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Estacion(codigo='%s')>" % (self.codigo)

class TableMagnitud(Base):
    __tablename__ = 'table_magnitud'
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, onupdate=datetime.now)
    codigo = Column(String)
    descripcion = Column(String(100))
    unidad = Column(String(8))
    estacion_magnitud = relationship('DatoEstacion', back_populates='table_magnitud')
    estacion_id = Column(Integer, ForeignKey('contaminacion_estacion.id'))
    table_contaminacion = relationship('TableContaminacion', back_populates='magnitud_contaminacion',
                                 cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Magnitud(codigo='%s', descripcion='%s', unidad='%s', estacion_magnitud='%s')>" % (self.codigo,
                                                                                                   self.descripcion,
                                                                                                   self.unidad ,
                                                                                                   self.estacion_magnitud)

class TableContaminacion(Base):
    __tablename__ = 'table_contaminacion'
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, onupdate=datetime.now)
    fecha = Column(DateTime)
    valor = Column(Float)
    validez = Column(String(1))
    magnitud_contaminacion = relationship('TableMagnitud', back_populates='table_contaminacion')
    magnitud_id = Column(Integer, ForeignKey('table_magnitud.id'))

    def __repr__(self):
        return "<Contaminacion(fecha='%s', valor='%s')>"%(self.fecha, self.valor)


mi_objeto = contaminacion()
mi_objeto.save_estaciones()
mi_objeto.save_magnitud()

while True:
     mi_objeto.save_contaminacion()
     sleep(3600)
