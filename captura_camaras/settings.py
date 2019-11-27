lista_camaras = [['0001', 'http://informo.munimadrid.es/cameras/Camara06303.jpg', 'S', '45.19','41.32', '0'],
                ['0002', 'http://informo.munimadrid.es/cameras/Camara06304.jg', 'S', '45.19','41.32', '0'],
                ['0003', 'http://informo.munimadrid.es/cameras/Camara06305.jpg', 'S', '45.19','41.32', '0'],
                ['0004', 'http://informo.munimadrid.es/cameras/Camara06306.jpg', 'S', '45.19','41.32', '0']]

version_scrap = "0.3.1"
version_a_s3 = "0.4"

# Variables para el crawler
headers = {'User-Agent': 'Crawler para Proyecto Estudiante Big Data - unai.herran@gmail.com'}

#Directorios
SCRAP_DIR = 'scrapped/'
PROCCESED_DIR = 'procesed/'

# Image parameters
OUTPUT_RESOLUTION_HEIGHT = 200  # Not Used
OUTPUT_RESOLUTION_WIDTH = 360   # Not Used

IMG_OUTPUT_FORMAT = "JPEG"

#Rekognizion
MAX_LABELS = 20
CONFIDENCE_LEVEL_LABEL = 60
CONFIDENCE_LEVEL_CAR = 60
