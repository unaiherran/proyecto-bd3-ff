from influxdb import InfluxDBClient
import settings

from datetime import datetime
from glob import glob
from time import sleep

class Monitor(object):
    def __init__(self):
        db_host = '3.248.232.251'
        db_port = 8086
        db_user = 'admin'
        db_password = 'influx2019'
        db_database = 'Monitor'
        self.client = InfluxDBClient(db_host, db_port, db_user, db_password, db_database)

    def define_json(self, measurement, time, fields):
        """
        :param measurement: lo que se está midiendo
        :param time: es un datetime
        :param fields: diccionario {"value": 0.64}
        :return: devuelve el json a almacenar en influx
        """
        # fields es un
        # time es datetime
        # measurement es lo que se está midiendo
        json_body = [
            {
                "measurement": [measurement],
                "tags": {
                    "provider": "KC-BD-FF",
                },
                "time": time.isoformat(),
                "fields": fields
            }
        ]
        return json_body

    def count_files(self, directory):
        lista_archivos = glob(directory)
        return len(lista_archivos)

    def write_to_influx(self):
        value_for_procesing = self.count_files(settings.PROCESS_DIR + '*')
        fields_for_procesing = {'value': value_for_procesing}
        
        # llamo al método define_json para construir el json a grabar
        json_body_for_procesing = self.define_json(measurement='Archivos en scrap', time=datetime.now(),
                                                   fields=fields_for_procesing)
        self.client.write_points(json_body_for_procesing)
        value_process = self.count_files(settings.SCRAP_DIR + '*')
        fields_process = {'value': value_process}
        json_body_process = self.define_json(measurement='Archivos procesados', time=datetime.now(), fields=fields_process)
        self.client.write_points(json_body_process)

while True:
    monitor = Monitor()
    monitor.write_to_influx()
    monitor.client.close()
    sleep(600)

