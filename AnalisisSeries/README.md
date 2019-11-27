# Documentación

Aquí se ha generado un notebook de jupiter para intentar analizar un poco los datos se las predicciones y ver que pinta tienen
se ha comenzado por hacer una representación gráfica de los cluster de forma interactiva. Se dispone de un slicer que permite ir
cambiando de cluster. 

También se han ploteado las graficas de diferencias entre valores así como el error relativo. Es un analisis muy por encima en el
que hay que seguir trabajando del que esta sacar datos relavantes como la estacionalidad etc. 

El objetivo sería poder aplicar a estas series temporales el modelo autoregresivo SARIMA para predecir los datos del dia siguiente
o incluso la semana siguiente.. de momento tenemos muy pocos datos para aplicarlo. Esta predicción se podría comparar
con nuestra predicción del deeplearning para ver como casan estos dós métodos.

El códico está compuesto por una clase con una serie de métodos que nos permiten realizar opciones de visualización.
Como dato de inicialización recibe un csv con los las fechas y los valores de la ocupación en el instante actual, la predicción 
dentro de 15 min y el valor real medido a los 15 min

En grafana también se monitorizan estos datos solo que debido a limitaciones se muestra el valor medio de todos los cluster, lo 
que nos permite saber si hay algún problema en la generación de estos datos.

Como métodos relevantes está el método "filter_data" para seleccionar los datos a partir de una fecha en concreto que se pasa como argumento

Otro método sería el "set_df" que sirve para decirle a la clase que datos debe coger ya que por defecto se settea con el dataset 
de entrada

y por último seria el método show_all que muestra las graficas.
