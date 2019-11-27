#!/usr/bin/python

import glob, os, sys
import argparse
import time
import settings
from secret import *

from datetime import datetime
from datetime import timedelta

import mysql.connector

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

import hashlib
from utils import setup_logger


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed


def is_processed(filename):
    # Basado en https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them

    # sacar el tamaño del archivo que estamos mirando.
    size = os.path.getsize(filename)
    # sacar el hash del primer chunk
    small_hash = get_hash(filename, first_chunk_only=True)
    # sacar el hash del archivo
    full_hash = get_hash(filename, first_chunk_only=False)

    respuesta = False

    # recorrer los archivos que hay en el directorio processed
    directorio = settings.PROCCESED_DIR + '*'

    for archivo in glob.glob(directorio):
        archivo_size = os.path.getsize(archivo)
        if size != archivo_size:
            # si el tamaño es distinto, seguir.
            continue
        else:
            # si el tamaño es el mismo comprobar hash de primer chunk
            archivo_small_hash = get_hash(archivo, first_chunk_only=True)
            print("Filename: %s Size: %s Small Hash: %s, Full_Hash= %s" % (filename, size, small_hash, full_hash))
            print("Comparado con Filename: %s Size: %s Small Hash: %s " % (archivo, archivo_size, archivo_small_hash))

            if small_hash != archivo_small_hash:
                # si el primer chunk es distinto continuar
                continue
            else:
                # si es el mismo calcular el hash del archivo
                archivo_full_hash = get_hash(archivo, first_chunk_only=False)
                if full_hash != archivo_full_hash:
                    # si es distinto continuar
                    continue
                else:
                    # si es el mismo salir del bucle y devolver true
                    respuesta = True
                    break

    # cuando termina el bucle devolver False
    return respuesta


def count_cars(photo, bucket):

    client = boto3.client('rekognition')
    max_labels = settings.MAX_LABELS
    try:
        response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=max_labels)
    except ClientError:
        print('ERROR EN LA RESPUESTA')
        return 999999,'IMAGE INVALID. DO NOT SAVE.'

    number_of_cars = 0

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        for label in response['Labels']:
            if label['Name'] == 'Car':
                if label['Confidence'] >= settings.CONFIDENCE_LEVEL_LABEL:
                    lista_coches = label['Instances']
                    for coches in lista_coches:
                        if coches['Confidence'] >= settings.CONFIDENCE_LEVEL_CAR:
                            number_of_cars += 1
    else:
        number_of_cars = 9999

    return number_of_cars, response


def process_files(process_logger, verbose=False):

    # Si no existe process dir, crearlo
    if not os.path.isdir(settings.PROCCESED_DIR):
        os.mkdir(settings.PROCCESED_DIR)
        mensaje = 'No existe el directorio %s. Se crea' % settings.PROCCESED_DIR
        process_logger.info(mensaje)
        if verbose:
            print(mensaje)

    directorio = settings.SCRAP_DIR + '*'
    longitud_scrap_dir = len(settings.SCRAP_DIR)

    # setting Amazon Bucket
    s3 = boto3.resource('s3',
                        config=Config(signature_version='s3v4')
                        )
    bucket_name = 'proyecto-bd3-ff'

    lista_archivos = glob.glob(directorio)
    total_de_archivos = len(lista_archivos)

    if verbose:
        if total_de_archivos > 50:
            mensaje = f'Quedan {total_de_archivos} por procesar. Proceso sólo 50'
        else:
            mensaje = f'Quedan {total_de_archivos}. Los porceso'
        print(mensaje)
        process_logger.info(mensaje)

    lista_archivos = lista_archivos[0:50]
    total_de_archivos = len(lista_archivos)

    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_database,
        port=db_port
    )

    i = 0

    for file in lista_archivos:
        i += 1

        file_name = file[longitud_scrap_dir:]

        # Mirar si esta ya procesado (tamaño, small hash y full hash)
        if not is_processed(file):
            skip = False
            # copiar a amazon s3
            data = open(file, "rb")
            key = 'camera_images/' + file_name
            try:
                s3.Bucket(bucket_name).put_object(Key=key, Body=data)
                mensaje = '(%s/%s) %s subido a bucket %s/camera_images' % (i, total_de_archivos, file_name, bucket_name)
                process_logger.info(mensaje)

            except ClientError:
                skip = True
                mensaje = f'{file_name} no ha sido subido. Lo intento en otro momento'
                process_logger.error(mensaje)

            if verbose:
                print(mensaje)

            # pasarlo por rekognize
            if not skip:
                num_cars, response = count_cars(key, bucket_name)
                if response == 'IMAGE INVALID. DO NOT SAVE.':
                    skip = True

            if not skip:
                # escribir en BDD
                if connection.is_connected():
                    cursor = connection.cursor()
                    nombre_separado = file_name.split('_')
                    id_camara = nombre_separado[0]
                    fecha_str = nombre_separado[1] + '_' + nombre_separado[2]
                    fecha_imagen = 'STR_TO_DATE("{}", "%Y%m%d_%H%i.jpg")'.format(fecha_str)

                    sql = f'INSERT INTO ImagenesCamarasTrafico(id_camara,imagen,response,num_cars,fecha) values ' \
                          f'({id_camara}, "{key}", "{response}", {num_cars}, {fecha_imagen});'

                    mini_sql = f'INSERT INTO ImagenesCamarasTrafico(id_camara,imagen,response,num_cars,fecha) values ' \
                          f'({id_camara}, "{key}", "[response]", {num_cars}, {fecha_imagen});'
                    cursor.execute(sql)

                    connection.commit()
                    if verbose:
                        pass
                        #print(mini_sql)

                    process_logger.info(mini_sql)

                    # mover a directorio de procesado
                    destino = settings.PROCCESED_DIR + file_name
                    os.rename(file, destino)
                    mensaje = '\t %s movido a processed/%s' % (file, file_name)
                    process_logger.info(mensaje)
                    if verbose:
                        print(mensaje)

        else:
            # borrar archivo para no procesarlo otra vez)
            os.remove(file)
            mensaje = '\t %s ya estaba procesado, asi que lo borro' % file
            process_logger.info(mensaje)
            if verbose:
                print(mensaje)


def delete_old_files(minutes=30, verbose=False):
    directorio = settings.PROCCESED_DIR + '*'
    max_time = time.time() - (minutes * 60)

    for archivo in glob.glob(directorio):
        fecha = os.path.getmtime(archivo)

        if fecha < max_time:
            os.remove(archivo)
            if verbose:
                print('Borrando archivo: %s' % archivo)
                print('Fecha del archivo: %s, \nFecha máxima: max_time %s' % (time.strftime('%Y-%m-%dT%H:%M:%S',
                                                                                            time.localtime(fecha)),
                                                                              time.strftime('%Y-%m-%dT%H:%M:%S',
                                                                                            time.localtime(max_time))))


def move_log_to_s3(log_copiado, logger):
    ahora = datetime.now()
    ayer = ahora - timedelta(days=1)

    # PAra DEBUG
    # ayer = ahora - timedelta(minutes=1)

    if log_copiado < ayer:
        print('tengo que copiar')
        # copy log to s3
        s3 = boto3.resource('s3',
                            config=Config(signature_version='s3v4')
                            )
        bucket_name = 'proyecto-bd3-ff'

        data = open('to_s3.log', "rb")
        key = 'logs/to_s3_' + ahora.strftime('%Y-%m-%dT%H:%M:%S') + '.log'

        s3.Bucket(bucket_name).put_object(Key=key, Body=data)

        # delete log
        os.remove('to_s3.log')
        # new logger
        logger = setup_logger('to_s3_log', 'to_s3.log')
        logger.info (f'Log copiado a S3: {key}')
        # actualizar hora de copia
        log_copiado = ahora

    return log_copiado, logger


def main():
    descripcion = """Esta es la ayuda del script"""

    to_s3_logger = setup_logger('to_s3_log', 'to_s3.log')

    parser = argparse.ArgumentParser(description=descripcion)
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-v", "--verbose", help="", action="store_true")

    log_copiado = datetime.now()

    # read arguments from the command line
    args = parser.parse_args()

    # check for --version or -V
    if args.version:
        print("Send to S3 Camaras de Open Data Madrid, version", settings.version_a_s3)

    if args.verbose:
        verbose = True
    else:
        verbose = False

    while True:
        process_files(to_s3_logger, verbose=verbose)
        delete_old_files(minutes=15, verbose=verbose)
        log_copiado, to_s3_logger = move_log_to_s3(log_copiado, to_s3_logger)

        if verbose:
            print('Esperando un rato...(1 segundo)')
        to_s3_logger.info('Esperando 1 segundo')
        time.sleep(1)
        to_s3_logger.info('Otra vuelta')

if __name__ == '__main__':
    main()
