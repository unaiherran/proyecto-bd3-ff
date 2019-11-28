# Datos de tráfico en tiempo real

La obtención de los datos de tráfico en tiempo real se realiza en dos pasos:

## Descarga del xml del ayuntamiento de Madrid

El ayuntamiento de madrid provee de un API con un endpoint que ofrece los datos recopilados de los sensores de tráfico que tiene repartidos por toda la ciudad. 
La direción del endpoint es http://informo.munimadrid.es/informo/tmadrid/pm.xml y los datos se actualizan con una periocidad aproximada de 5 minutos. 
Cada actualización de los datos retorna mas de 4.000 registros.

El script **download_traffic_realtime.py** es el encarado de consumir estos datos. Cada 5 minutos realiza una consulta al endpoint para obtener los datos. Los datos obtenidos los graba en un fichero CVS que se almacena nombrandolo con la hora de las mediciones de los sensores.

Por otro lado está el proceso **merge_csv_files.py** que lee los ficheros csv generados por el anterior proceso y los graba en la base de datos MySQL. Antes de realizar la grabación de los datos realiza algunas acciones como generar campos para el dia de la semana o la hora, además de filtrar algunos datos que detectamos que en ocasiones venían mal y podían causar problemas futuros. 

Por otro lado está un sencillo script (**import_sensores.py**) que importa en la base de datos el catalogo de sensores de tráfico del ayuntamiento de Madrid
