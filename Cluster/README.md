# Custerización

Cuando vimos todos los datos que tendriamos que procesar nos dimos
cuenta que para obtener un modelo de la ciudad de Madrid era necesario
agrupar las medidas por area geografica. 

Aunque a primera vista no es evidente, si te paras a analizar un poco la
situación, esto es un problema de clusterización, simplemente aplicado a
las coordenadas geolocalizadas.

En el cuaderno `Clusterización Camaras-Sensores.ipynb` se puede ver los
experimentos realizados, pero a la hora de implementar todo en el
servidor se ha usado `coordenadas_a_cluster.py`. En ese script lo que se
hace es, con las coordenadas de todos los sensores y de las camaras,
generar un modelo de 200 clusters que, aplicado a otras coordenadas,
como las de los eventos nos indican a que grupo (o cluster) pertenece
ese evento.

## Aplicacion para todos los conjuntos de datos

En `poner_cluster_en_db.py` se implementan distintas funciones para ir
poblando la base de datos de toda la información relativa al clustering
elegido.

- `poblar_cluster()`

  Después de haber generado el modelo con `coordenadas_a_cluster.py` es
  necesario obtener las coordenadas del centro de ese cluster, para
  poder representarlo. Esto se realiza con
  `modelo.cluster_centers_.tolist()` y luego se graba en la base de
  datos.
  
- `clusterizar_sensores()` , `clusterizar_camaras()` y `clusterizar_eventos()`

  Asigna a cada sensor, cámara y eventoun cluster determinado según el
  modelo y lo guarda en la base de datos.
  
- Contaminación y Estaciones Meteorológicas.

  Para estos parametros la situación es ligeramente distinta, ya que una
  estación de medición afecta a distintos clusters. Por ello, se asignan
  las lecturas de esa estación al cluster más cercano.
  
  Con `tiempo_a_cluster()` y `contaminacion_a_cluster()` obtenemos las
  coordenadas de cada estación de medición y asignamos a cada cluster
  (tabla de cluster en db) el más cercano.
  
- Grandes Eventos

  Los grandes eventos afectan más a la circulación que los eventos
  normales, con lo que para modelarlos se ha usado una técnica distinta
  a los eventos. 
  
  Así pues, en `clusterizar_gran_evento()` a cada Gran Evento le
  asignamos el cluster que le corresponda, aplicando el modelo generado,
  pero, además le asignamos que clusters cercanos pueden estar afectados
  por ese evento.
  
Toda esta modelización es modificable si consideramos que necesitamos
más resolución cambiando el número de clusters, y reentrenando el modelo
de clustering.


