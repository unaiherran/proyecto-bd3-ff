#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
import lxml.etree as etree
import pandas as pd
from io import StringIO
import time
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
Base = declarative_base()

class contaminacion(object):

    def __init__(self):
        self.url_txt = "https://datos.madrid.es/egob/catalogo/212531-7916318-calidad-aire-tiempo-real.txt"

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

    def save_data(self):
        df = self.get_txt()
        db = BaseOne('proyecto')
        session = db.sesion_inicio()

        # Query que devuelve todos los datos de la tabla
        for index, value in df.iterrows():
            fila = df.iloc[index]
            provincia = str(fila['PROVINCIA'])
            municipio = str(fila['MUNICIPIO'])
            estacion = str(fila['ESTACION'])
            magnitud = str(fila['MAGNITUD'])
            punto = str(fila['PUNTO'])
            ano = str(fila['ANO'])
            mes = str(fila['MES'])
            dia = str(fila['DIA'])
            h01 = float(fila['H01'])
            v01 = str(fila['V01'])
            h02 = float(fila['H02'])
            v02 = str(fila['V02'])
            h03 = float(fila['H03'])
            v03 = str(fila['V03'])
            h04 = float(fila['H04'])
            v04 = str(fila['V04'])
            h05 = float(fila['H05'])
            v05 = str(fila['V05'])
            h06 = float(fila['H06'])
            v06 = str(fila['V06'])
            h07 = float(fila['H07'])
            v07 = str(fila['V07'])
            h08 = float(fila['H08'])
            v08 = str(fila['V08'])
            h09 = float(fila['H09'])
            v09 = str(fila['V09'])
            h10 = float(fila['H10'])
            v10 = str(fila['V10'])
            h11 = float(fila['H11'])
            v11 = str(fila['V11'])
            h12 = float(fila['H12'])
            v12 = str(fila['V12'])
            h13 = float(fila['H13'])
            v13 = str(fila['V13'])
            h14 = float(fila['H14'])
            v14 = str(fila['V14'])
            h15 = float(fila['H15'])
            v15 = str(fila['V15'])
            h16 = float(fila['H16'])
            v16 = str(fila['V16'])
            h17 = float(fila['H17'])
            v17 = str(fila['V17'])
            h18 = float(fila['H18'])
            v18 = str(fila['V18'])
            h19 = float(fila['H19'])
            v19 = str(fila['V19'])
            h20 = float(fila['H20'])
            v20 = str(fila['V20'])
            h21 = float(fila['H21'])
            v21 = str(fila['V21'])
            h22 = float(fila['H22'])
            v22 = str(fila['V22'])
            h23 = float(fila['H23'])
            v23 = str(fila['V23'])
            h24 = float(fila['H24'])
            v24 = str(fila['V24'])

            try:
                test = session.query(DatoContaminacion).get(session.query(DatoContaminacion).filter(DatoContaminacion.dia == dia,
                                                           DatoContaminacion.magnitud == magnitud,
                                                           DatoContaminacion.punto == punto,
                                                           DatoContaminacion.estacion == estacion,
                                                           DatoContaminacion.ano == ano,
                                                           DatoContaminacion.mes == mes).first().id)

                query = session.query(DatoContaminacion).filter(DatoContaminacion.dia == dia,
                                                           DatoContaminacion.magnitud == magnitud,
                                                           DatoContaminacion.punto == punto,
                                                           DatoContaminacion.estacion == estacion,
                                                           DatoContaminacion.ano == ano,
                                                           DatoContaminacion.mes == mes)


                query.update({'h01': h01, 'h02': h02, 'h03': h03, 'h04': h04, 'h05': h05, 'h06': h06, 'h07': h07,
                              'h08': h08, 'h09': h09, 'h10': h10, 'h11': h11, 'h12': h12, 'h13': h13, 'h14': h14,
                              'h15': h15, 'h16': h16, 'h17': h17, 'h18': h18, 'h19': h19, 'h20': h20, 'h21': h21,
                              'h22': h22, 'h23': h23, 'h24': h24, 'v01': v01, 'v02': v02, 'v03': v03, 'v04': v04,
                              'v05': v05, 'v06': v06, 'v07': v07, 'v08': v08, 'v09': v09, 'v10': v10, 'v11': v11,
                              'v12': v12, 'v13': v13, 'v14': h14, 'v15': v15, 'v16': v16, 'v17': v17, 'v18': v18,
                              'v19': v19, 'v20': v20, 'v21': v21, 'v22': v22, 'v23': h23, 'v24': h24})

            except:
                print('Creo la tabla')
                data = DatoContaminacion(provincia=provincia, municipio=municipio, estacion=estacion,
                                            magnitud=magnitud, punto=punto, ano=ano, mes=mes, dia=dia, h01=h01, v01=v01,
                                            h02= h02, v02=v02, h03=h03, h04=h04, h05=h05, h06=h06, h07=h07, h08=h08,
                                            h09=h09, h10=h10, h11=h11, h12=h12, h13=h13, h14=h14, h15=h15, h16=h16,
                                            h17=h17, h18=h18, h19=h19, h20=h20, h21=h21, h22=h22, h23=h23, h24=h24)
                session.add(data)

        session.commit()
        session.close()

    def print_table(self):
        db = BaseOne('proyecto')
        db.inspect()


class BaseOne(object):
    def __init__(self, nombre_base):

        # # Esta sera la base de datos general con las configuraciones
        # self.motor = create_engine('sqlite:///./' + nombre_base)
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

class DatoContaminacion(Base):
    __tablename__='contaminacion'
    id = Column(Integer, primary_key=True)
    provincia = Column(String)
    municipio = Column(String)
    estacion = Column(String)
    magnitud = Column(String)
    punto = Column(String)
    ano = Column(String)
    mes = Column(String)
    dia = Column(String)
    h01 = Column(Float)
    v01 = Column(String)
    h02 = Column(Float)
    v02 = Column(String)
    h03 = Column(Float)
    v03 = Column(String)
    h04 = Column(Float)
    v04 = Column(String)
    h05 = Column(Float)
    v05 = Column(String)
    h06 = Column(Float)
    v06 = Column(String)
    h07 = Column(Float)
    v07 = Column(String)
    h08 = Column(Float)
    v08 = Column(String)
    h09 = Column(Float)
    v09 = Column(String)
    h10 = Column(Float)
    v10 = Column(String)
    h11 = Column(Float)
    v11 = Column(String)
    h12 = Column(Float)
    v12 = Column(String)
    h13 = Column(Float)
    v13 = Column(String)
    h14 = Column(Float)
    v14 = Column(String)
    h15 = Column(Float)
    v15 = Column(String)
    h16 = Column(Float)
    v16 = Column(String)
    h17 = Column(Float)
    v17 = Column(String)
    h18 = Column(Float)
    v18 = Column(String)
    h19 = Column(Float)
    v19 = Column(String)
    h20 = Column(Float)
    v20 = Column(String)
    h21 = Column(Float)
    v21 = Column(String)
    h22 = Column(Float)
    v22 = Column(String)
    h23 = Column(Float)
    v23 = Column(String)
    h24 = Column(Float)
    v24 = Column(String)


mi_objeto = contaminacion()
#mi_objeto.save_data()
mi_objeto.print_table()
