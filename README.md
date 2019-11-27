# Proyecto final BD3 KC - The Final Five

Este proyecto propone hacer un estudio y previsión del tráfico en las
calles de Madrid apoyandose en datos de distintos feeds de información.

Los distintos scripts creados estan organizados por directorios. Para
facilitar el trabajo de evaluación explicamos someramente que hay en
cada uno de ellos. Dentro de los directorios hay un `README.md` que
desarrolla más el contenido de cada uno

* `AnalisisSeries` - Aquí se ha generado un notebook de Jupyter para
  intentar analizar los datos de las predicciones de forma interactiva.
  
* `BD` - Información de como está construida la base de datos.

* `captura_camaras` - scrapea y analiza las imagenes publicas de las
  camaras de trafico de Madrid para contar el número de coches que hay
  en ellas.
  
* `Cluster` - Realiza la agrupación de los distintos sensores en
  conjuntos de datos para poder realizar el modelo

* `cluster-map-master`

* `Datos Contaminacion` - El objetivo principal en este módulo es la 
  extracción de datos sobre contaminación de la Provincia de Madríd
  procedientes de los datos abiertos del ayuntamiento de Madrid.

* `Datos Eventos` - Este modulo realiza la carga de los Eventos en la
  base de datos

* `DatosMeteorologicos` - El objetivo principal en este módulo es la
  extracción de datos metereológicos de la Provincia de Madríd
  procedentes de la pagina de AEMET

* `DatosTraficoTiemporeal` - Este modulo carga los datos procedentes de
  un endpoint del Ayuntamiento de Madrid con todos las lecturas de los
  sensores de Trafico y los incorpora a la base de datos para su
  posterior procesado.

* `Influx` - Este script guarda datos en InfluxDB sobre el número de
  archivos existente en dos directorios de almacenamiento de las
  imagenes de tráficos que son uno del scrapeo y otra para el procesado.
  Esto nos permitirá mediante la monitorización a través de grafana de
  ver si hay algún problema en la realización de estos procesos.

* `Modelo Deep Learning` - Analisis, decisión e implementación del
  modelo predictivo elegido.
  
* `Propuesta` - Documentación de la propuesta inicial, así como la
  presentación final del proyecto.

* `ServerLess` - 




# Links

## Trello
https://trello.com/finalfive01
https://trello.com/b/2HhvIpnH/proyecto

## Google Docs
https://drive.google.com/drive/folders/18vm9Fffha3DPhxDTHV2xVlHc1_JlPy8F?usp=sharing

## Github
https://github.com/unaiherran/proyecto-bd3-ff

## Presentacion
https://drive.google.com/file/d/1w3uv5nggkNfqA74Zh-Vb4uCUruXZc03H/view?usp=sharing
