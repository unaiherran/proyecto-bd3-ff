# proyecto-modelo

Con estos scripts hacemos tanto el procesado de los datos como las
tareas de entreno y prediccioón de los modelos.

## Procesado

```create_training_data.py```

Este script procesa todos los datos obtenidos por los distintos
scrappers y genera una tabla en la base de datos que luego usaremos
tanto para entrenar los modelos como para generar las predicciones en el
futuro.

Está compuesto de las siguientes funciones:

* `calcular_de_imagenes_camara(fecha)` 

  Realiza una consulta en los datos grabados de camaras para un periodo
  de 15 minutos, agrupa los resultados por clusters y genera un
  Dataframe con los valores de numero de coches minimo, maximo, media y
  mediana para cada cluster.

  Los valores de num_cars tienen un peso pequeño en la predicción, y el
  generarlos a través de Rekognitor, hace que los gastos de AWS sean muy
  altos, con lo que, aunque en un principio esten calculados, no los
  usemos en el modelo final. Se dejan en la función porque no cuesta
  mucho a la hora de calcular, y si en algún momento deseamos volverlos
  a usar sea relativamente fácil
   
* `calcular_de_datos_trafico(fecha):` 

  Selecciona todos los datos de trafico para un periodo determinado y
  además de calcular medias, minimos, maximos y mediana, tambien realiza
  un calculo de la media eliminando el 25%, 50%, 75% de los datos más
  bajos. Estos valores se generan para darle algo más de información al
  modelo y hacen que las predicciones sean más correctas.
  
* `calcular_de_eventos(fecha):`

  Los eventos que ocurren en un cluster se agrupan de una manera
  distinta a las lecturas en tiempo real de trafico y coches.
  Consideramos que un evento puede afectar a la circulación en un
  cluster no sólo a la hora a la que se realiza, sino en un periodo de
  tiempo anterior y posterior al mismo.
  
  Así pues, se calculan distintas variables para contar que los eventos
  ocurridos desde dos horas antes hasta una hora después del mismo y si
  son gratuitos o no.
  
* `calcular_de_gran_evento(fecha)`

  Los grandes eventos, (partidos de futbol, festivales, cumbres
  climaticas, huelgas de la EMT) no afectan sólo a un cluster, sino que
  lo hacen también a todos los clusters que estén en un radio
  determinado. En la tabla de grandes eventos se guardan a que cluster
  puede afectar ese gran evento, y se añade al dataframe para ese
  periodo de tiempo.


* `calcular_de_tiempo(fecha)`
 
  En el entorno de Madrid, hay unas cuantas estaciones meteorologicas,
  pero menos que clusters, con lo que a la hora de definir estos
  clusters, se les asigna la estación meteorologica más cercana y se
  considera que las lecturas de esta estación afectaran a todo el
  cluster.
  
* `calcular_de_fecha(fecha):`
 
  Calcula distintos parametros para esa fecha, que día de la semana es,
  que día del mes, si es festivo... y se lo asigna a cada cluster para
  incorporarlo al dataset de entrenamiento.
   
## Entrenamiento

Se han hecho varias pruebas con distintos modelos, tanto de ML como de
DL. Finalmente, el modelo que mejores resultados ha dado, se entrena con
todos los datos que tenemos, desde el 20-10-2019 hasta el 18-11-2019 con
los datos obtenidos del procesado.

Después de analizar distintos resultados, se decide que las variables
minima y maxima no tienen ninguna importancia, con lo que se eliminan
del dataset de entrenamiento.
 
Por los motivos economicos explicados anteriormente, se hace lo mismo
con num_cars. Si bien los resultados son peores que con esta variable,
el costo lo hace inviable.

El código está basado en los experimentos realizados en
`Generar_Dataset.ipynb` y adaptado a su funcionamiento como script de
Python `entrenar_modelo.py`.

Los datos procesados se guardan todos en una tabla de la base de datos
`grouped_data_0` y se separan en datos de entrenamiento con `separar
training y test.sql`.

Una vez tenemos ese dataset, lo cargamos, ordenado por fecha, eliminamos
las columnas que no nos interesan y separamos entre entrenamiento,
validacion y test (65%, 25% y 10%)

Nuestra variable objetivo se copia en el dataframe con un desplazamiento
de -1, pues lo que queremos predecir es con las variables de entrada el
comportamiento del trafico en el proximo periodo.

El modelo elegido es muy sencillo, una capa de LSTM y una capa densa:

<!-- language: lang-none -->

         +---------+
         | Datos   |
         +----+----+
              |
       +------+--------+
       | MaxMinScaler  |
       +------+--------+ 
              | 
          +---+----+ 
          |LSTM(50)|
          +---+----+ 
              | 
          +---+---+ 
          | Dense | 
          +---+---+ 
              | 
    +---------+----------+
    | Predicción escalada| 
    +---------+----------+ 
              |
      +-------+--------+
      |MaxMinScalerInv | 
      +-------+--------+ 
              | 
         +----+-----+ 
         |Predicción|
         +----------+

Como el LSTM necesita los datos en una escala de 0 a 1 usamos además una
función de escalado antes y despues de la red.
 
Después de entrenar el modelo, con los datos de tarin y validación,
evaluamos la idionidad del mismo con el conjunto de test separado
anteriormente, el 10% del conjunto inicial del dataframe usado para
entrenar.

Se han hecho distintos experimentos para distintas variables objetivos y
usando distintas variables. Como esos experimentos eran largos, se
programo un batch que evaluaba el RMSE para los distintos conjuntos de
variables y lo almacenaba en un csv (`resultado.csv`).

Una vez vistos esos resultados, se eligio un modelo, y se entrenó un
modelo para cada cluster (Con un split de 75,25) y se almacenó en el
directorio `/modelo`.

## Predicción

Con los modelos entrenados se generan predicciones para todos los
datasets con `fill_predict_table.py`

Primero se carga el modelo y el scaler a usar, y se eliminan las
columnas no usadas.

Una vez hecho esto, simplemente hay que aplica el scaler, lanzar la
prediccion del modelo y aplicar el scaler inverso.
 

## Predicción en tiempo real

`real_time_predict.py` 

Así como la predicción anterior era para todo el
dataset, queremos hacer un script de python que generará predicciones en
tiempo real para mostrar en la visualización.

El código es practicamente igual que el de predicción, pero en lugar de
evaluar una matriz enorme con todas los datos, se hace con una matriz 
pequeña con sólo los datos del último cuarto de hora.

Se ejecuta mediante un cronjob cada 5 minutos, en el servidor de
predicciones.

## Comprobación de predicción

`sacar_medidas_reales_para_predict.py`

Cuando se hace la predicción aun no tenemos acceso a los datos futuros,
por ello, una vez ya tenemos lecturas de los sensores actualizamos los
registros con la lectura real. Sirve para comparar la prediccion con la
realidad. Se ejecuta con un cronjob cada 10 minutos en el servidor de
predicciones

