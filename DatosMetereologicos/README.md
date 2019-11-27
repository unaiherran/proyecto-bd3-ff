# Documentación

## Objetivo
El objetivo principal en este módulo es la extracción de datos metereológicos de la Provincia de Madríd procedentes de la pagina de Aemet

## Librerías
Para el manejo de la base de datos empleo el ORM sqlalchemy que permite interactuar con la base de datos como si fuesen objetos
mientras que para el manejo de los datos empleo pandas

## DOC
El scrip para obtener los datos de la AEMET consta de una clase donde se encuentran implementados los métodos necearios para extraer los datos metereológicos y guardarlos en la base de datos. Puesto que los datos de la pagina se actualizan cada hora este script se ejecuta cada hora para grabar los datos recientes en la base.

El script consta de una clase llamada aemet que consta de una seríe de métodos que se encargan de obtener los datos y guardarlos en la base correctamente. Estós datos serán monitorizados posteriormente con grafana para ver su evolución en el tiempo.

Los datos son extraidos a través del API de la aemet. En la base de datos creo dos tablas. La primera llamada "EstaciónTiempo"
almacena los datos de la estación: codigo de la estación, longitud, latitu y ubicación. Estos datos permitirán situarlas en un mapa. Hay un total de 10 estaciones en Madríd pero útiles para el proyecto solo serían 3 ya que las otras se encuentran muy alejadas del centro de Madríd en zonas que no son de interes.

La otra tabla que guardo en la base se llama "MedidaTiempo2" que tiene una foreingKey a la tabla anterior para poder relacionarlas. Esta tabla es la que guardara las medidas de cada estación. Hay montón de variables, muchas con valor null para determinadas estaciones pero que se guardan de todas manera porque no cuesta nada tenerlas ahí. De todas la varibles las más relevantes serían la temperatura ambiente y las precipitaciónes.

Así que el primer paso es rellenar la tabla de las estaciones para lo cual llamamos al método de la clase 


