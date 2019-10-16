#!/usr/bin/python

import glob, os, sys
import argparse
import time
import settings

import boto3
from botocore.client import Config

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


def process_files(verbose=False):

    process_logger = setup_logger('process_log', 'process_image.log')
    directorio = settings.SCRAP_DIR + '*'
    longitud_scrap_dir = len(settings.SCRAP_DIR)

    # setting Amazon Bucket
    s3 = boto3.resource('s3',
                        config=Config(signature_version='s3v4')
                        )
    bucket_name = 'proyecto-bd3-ff'

    for file in glob.glob(directorio):
        file_name = file[longitud_scrap_dir:]

        # Mirar si esta ya procesado (tamaño, small hash y full hash)
        if not is_processed(file):
            # copiar a amazon
            data = open(file, "rb")
            key = 'camera_images/'+file_name
            s3.Bucket(bucket_name).put_object(Key=key, Body=data)
            mensaje = '%s subido a bucket %s/camera_images' %(file_name, bucket_name)
            process_logger.info(mensaje)
            if verbose:
                print(mensaje)

            # mover a directorio de procesado
            destino = settings.PROCCESED_DIR + file_name
            os.rename(file, destino)
            mensaje = '%s movido a processed/%s' %(file, file_name)
            process_logger.info(mensaje)
            if verbose:
                print(mensaje)

        else:
            # borrar archivo para no procesarlo otra vez)
            os.remove(file)
            mensaje = '%s ya estaba procesado, asi que lo borro' %file
            process_logger.info(mensaje)
            if verbose:
                print(mensaje)


def delete_old_files(minutes=30, verbose=False):
    directorio = settings.PROCCESED_DIR + '*'
    max_time = time.time() + (minutes*60)

    for archivo in glob.glob(directorio):
        fecha = os.path.getmtime(archivo)

        if fecha < max_time:
            os.remove(archivo)

def main():
    descripcion = """Esta es la ayuda del script"""

    to_s3_logger = setup_logger('to_s3_log', 'to_s3.log')

    parser = argparse.ArgumentParser(description=descripcion)
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-v", "--verbose", help="", action="store_true")

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
        process_files(verbose=verbose)
        delete_old_files(minutes=30, verbose=verbose)
        time.sleep(10)

if __name__ == '__main__':
    main()
