import boto3
import pprint
import settings

import secret

test_path = 's3://proyecto-bd3-ff/camera_images/01301_20191019_2127.jpg'


def count_cars(photo, bucket):

    client = boto3.client('rekognition')
    max_labels = settings.MAX_LABELS

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=max_labels)

    number_of_cars = 0

    print(response['ResponseMetadata']['HTTPStatusCode'])

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


def actualiza_camaras_en_db():
    pass

def main():
    photo = 'camera_images/01301_20191019_2127.jpg'
    bucket = 'proyecto-bd3-ff'
    num_cars, response = count_cars(photo, bucket)
    print(num_cars)

main()