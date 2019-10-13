import logging
import time

import requests
from xml.etree import ElementTree
import csv

logging.basicConfig(level=logging.INFO, filename='traffic_realtime.log', filemode='a', format='%(asctime)s - %(message)s')

if __name__ == "__main__":
    while True:
        logging.info('Downloading realtime traffic data ...')
        real_time = requests.get('http://informo.munimadrid.es/informo/tmadrid/pm.xml')
        root = ElementTree.fromstring(real_time.content)

        logging.info('Data downloaded')

        child = root.find('fecha_hora')
        fecha = child.text

        data = []
        csv_columns = [
            'idelem',
            'fecha',
            'descripcion',
            'accesoAsociado',
            'intensidad',
            'ocupacion',
            'carga',
            'nivelServicio',
            'intensidadSat',
            'error',
            'subarea',
            'st_x',
            'st_y']

        for pm in root.iter('pm'):
          #print(child.tag, child.text)
          obj = {}
          obj['idelem'] = pm.find('idelem').text
          obj['fecha'] = fecha
          if pm.find('descripcion'): obj['descripcion'] = pm.find('descripcion').text
          if pm.find('accesoAsociado'): obj['accesoAsociado'] = pm.find('accesoAsociado').text
          obj['intensidad'] = pm.find('intensidad').text
          obj['ocupacion'] = pm.find('ocupacion').text
          obj['carga'] = pm.find('carga').text
          obj['nivelServicio'] = pm.find('nivelServicio').text
          if pm.find('intensidadSat'): obj['intensidadSat'] = pm.find('intensidadSat').text
          obj['error'] = pm.find('error').text
          if pm.find('subarea'): obj['subarea'] = pm.find('subarea').text
          obj['st_x'] = pm.find('st_x').text
          obj['st_y'] = pm.find('st_y').text
          data.append(obj)

        csv_file = f"real_time{fecha.replace('/', '-').replace(':', '_')}.csv"

        logging.info(f'Writing {len(data)} rows in {csv_file}')
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in data:
                    writer.writerow(data)
        except IOError:
            print("I/O error")

        logging.info('File writed')

        time.sleep(300)


