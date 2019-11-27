# Documentación

## Objetivo
El objetivo de este script es guardar datos en influxdb sobre el número de archivos existente en dos directorios de 
almacenamiento de las imagenes de tráficos que son uno del scrapeo y otra para el procesado. Esto nos permitirá mediante la
monitorización a través de grafana de ver si hay algún problema en la realización de estos procesos.

Es un script muy sencillo que consta de una clase con tres métodos:
* **define_json** que se encarga de construir el json que será escrito en la base
* **count_files** que toma como argumento un directorio y cuenta el número de ficheros que hay
* **write_to_influx** que se encarga de escribir el json anterior a la base

