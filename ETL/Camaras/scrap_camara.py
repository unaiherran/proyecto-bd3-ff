#!/usr/bin/python

import sys, getopt
import argparse

import requests
import settings
from PIL import Image
from io import BytesIO

from datetime import datetime

import csv

from utils import setup_logger


def crawl(lista_camaras = settings.lista_camaras, status_req = 0, verbose = False):
    output_list = []

    logger = setup_logger('crawler_log', 'crawler.log')

    errores = 0
    adquiridos = 0

    total_de_camaras = len(lista_camaras)
    i = 0

    # For each camera
    for camera in lista_camaras:
        i += 1
        address = camera[1]
        status = int(camera[5])

        now = datetime.now()
        fecha_str = str(now.year) + str(now.month) + str(now.day) + '_' + str(now.hour) + str(now.minute)

        name = settings.SCRAP_DIR + camera[0] + '_' + fecha_str + '.jpg'

        if status <= status_req:
            # conectarte a la url
            response = requests.get(address, settings.headers)
            if verbose:
                print('Leyendo Feed (%s/%s): %s' %(i, total_de_camaras,address))

            # gestion de errores HTTP

            if response.status_code >= 500:  # Server error
                # cambiar el estatus de la camara
                status += 100
                errores += 1
                logger.error('Camera: %s Feed %s da un error %s. Nuevo Status: %s', camera[0], camera[1],
                              response.status_code, status)
                if verbose:
                    print('ERROR: Camera: %s Feed %s da un error %s. Nuevo Status: %s', camera[0], camera[1],
                              response.status_code, status)

            elif response.status_code >= 400:  # Client Error
                status += 10
                errores += 1
                logger.error('Camera: %s Feed %s da un error %s.  Nuevo Status: %s', camera[0], camera[1],
                              response.status_code, status)
                if verbose:
                    print('ERROR: Camera: %s Feed %s da un error %s. Nuevo Status: %s', camera[0], camera[1],
                              response.status_code, status)

            elif response.status_code == 200:
                # ver si es imagen

                try:
                    img = Image.open(BytesIO(response.content))
                    # resize file
                    # Probablemente se tenga que hacer en otro proceso
                    #img = img.resize((settings.OUTPUT_RESOLUTION_WIDTH, settings.OUTPUT_RESOLUTION_HEIGHT),
                    #                 Image.ANTIALIAS)
                    # save image
                    img.save(name, settings.IMG_OUTPUT_FORMAT)
                    adquiridos += 1

                    if status > 0:
                        status = status - 1

                    logger.info('Camera: %s Feed %s graba la imagen Nuevo Status: %s', camera[0], camera[1], status)

                except IOError:
                    status += 1  # archivo no es imagen
                    errores += 1
                    logger.error('Camera: %s Feed %s, no es una imagen válida. Nuevo Status: %s',
                                 camera[0], camera[1], status)
                    if verbose:
                        print('ERROR: Camera: %s Feed %s, no es una imagen válida. Nuevo Status: %s',
                                 camera[0], camera[1], status)

        e = [camera[0], camera[1], camera[2], camera[3], camera[4], str(status)]

        output_list.append(e)

    return output_list, errores, adquiridos


def leer_listado_camaras(file_name="lista_camaras.csv"):
    """ Lee el listado de camaras de un archivo csv. si no tines este listado se obtiene despues de ejecutar
    sacar_listado.py"""

    with open(file_name, newline='') as file:
        reader = csv.reader(file)
        l = list(map(tuple, reader))
    return l


def scrap_video():
    # TODO De momento no hay nada, si sobra tiempo puedo intentar hacerlo
    pass


def actualizar_listado_camaras(l, file_name = "lista_camaras1.csv"):
    """Actualiza el csv del listado de camaras para el siguiente crawl. Graba el archivo segun el nombre que le pases
    en el parametro file_name"""

    with open(file_name, 'w', newline='\n') as myfile:
        wr = csv.writer(myfile, lineterminator='\n')
        for e in l:
            wr.writerow(e)


def main():
    descripcion = """Esta es la ayuda del script"""

    scrap_logger = setup_logger('scrap_camara_log', 'scrap_camera.log')

    parser = argparse.ArgumentParser(description=descripcion)
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-I", "--input", help="CSV file with list of cameras")
    parser.add_argument("-O", "--output", help="Output CSV file with list of cameras with updated success level")
    parser.add_argument("-s", "--status_requested", help="status requested (0, las que responden siempre)")
    parser.add_argument("-v", "--verbose", help="", action="store_true")

    # read arguments from the command line
    args = parser.parse_args()

    # check for --version or -V
    if args.version:
        print("Scrap Camaras de Open Data Madrid, version", settings.version_scrapp)

    if args.input:
        inputfile = args.input
        #todo comprobar que existe el fichero

    else:
        inputfile = 'lista_camaras.csv'

    if args.output:
        outputfile = args.output
    elif args.input:
        outputfile = inputfile
    else:
        outputfile = 'lista_camaras_test_out.csv'

    if args.status_requested:
        status_requested = int(args.status_requested)
    else:
        status_requested = 0

    if args.verbose:
        verbose = True
    else:
        verbose = False

    inicio = datetime.now()

    scrap_logger.info('Input file is: %s' %(inputfile))
    scrap_logger.info('Output file is %s' %(outputfile))
    scrap_logger.info('Status requested is %s' %(status_requested))
    scrap_logger.info('Inicio del scrap %s' %(inicio))
    if verbose:
        print('Input file is', inputfile)
        print('Output file is', outputfile)
        print('status requested is', status_requested)
        print('Inicio del scrap', inicio)

    lista_camara = leer_listado_camaras(inputfile)

    # lanza el crawler y devuelve una lista actualizada
    lista_camara_actualizada, errores, adquiridos = crawl(lista_camaras=lista_camara, status_req=status_requested,
                                                          verbose=verbose)

    resultado_crawl = "De %s pedidos, se han adquirido %s imagenes, con %s errores" %(len(lista_camara), adquiridos,
                                                                                      errores)

    if verbose:
        print(resultado_crawl)

    if errores:
        scrap_logger.warning(resultado_crawl)
    else:
        scrap_logger.info(resultado_crawl)

    # escribe la lista actualizada para el siguiente crawl
    actualizar_listado_camaras(lista_camara_actualizada, file_name=outputfile)

    fin = datetime.now()
    duracion = fin - inicio

    scrap_logger.info('Fin del Scrap %s' %(fin))
    scrap_logger.info('INFO: Me ha costado hacer el crawl %s' %(str(duracion)))
    if verbose:
        print('Fin de la operación',fin)
        print('Duración', duracion)


if __name__ == '__main__':
    main()
