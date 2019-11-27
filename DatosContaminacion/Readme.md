#Documentación
## Objetivo
El objetivo principal en este módulo es la extracción de datos sobre contaminación de la Provincia de Madríd procedientes de los datos abiertos del ayuntamiento de Madrid

## Librerías
Para el manejo de la base de datos empleo el ORM sqlalchemy que permite interactuar con la base de datos como si fuesen objetos mientras que para el manejo de los datos empleo pandas

## Funcionamiento
Se crean 3 tablas en la base de datos:
* "contaminacion_estacion" que guarda los datos relativos a la estación. El codigo, dirección, longitud, latitud etc que permite representarla en un mapa
* "Table_magnitud": esta tabla tiene una foreingKey a la tabla anterior y guarda el codigo del tipo de medida que realiza la estación así como una descripción y las unidades de medida.
* "table_contaminacion": por ultimo, esta tabla tiene una foreingKey a la tabla anterior y es donde se guarda la fecha de registro, el valor de la magnitud y si es válida.

Todas las tablas tienen dos campos a mayores uno de "create_at" que se crea cuando se realiza el registro inicial y otro de 
"modified_at" que controla cuando se ha modificado por última vez ese registro.

La aemet dispone de varios formatos de descarga de datos, csv y txt para lo cual están implementados sendos métodos que se encargan de devolver un dataframe de estos datos.

Me he decantado por emplear los datos del fichero txt ya que en el formato csv se incluia una magnitud que se encontraba en periodo de prueba y que en el formato txt no la han metido aún, esto me causaba algún problema cuando se encontraba con ella por lo que para no complicarme me he quedado con el fichero txt.

Como voy a tener valores en el tiempo los datos de las fechas hay que pasarlos a formato datetime a la hora de guardarlos en la base de datos, para ello se encuentra el método "make_date" que recibe un string y lo convierte a datetime.

La primera tabla en rellenar el la correspondiente a las estaciones para ello se ejecuta el método "save_estaciones". Esta solo se ejecuta una vez ya que no habrá cambios en principio. Aunque en un futuro si los podría haber.

La siguiente tabla es la de las magnitudes que tambien se ejecuta una sola vez y que se haría a través del método "save_magnitud".

Por último, ya solo queda guardar los valores de las variables cada hora en la tabla de contaminación
