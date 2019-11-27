# Proceso de carga de eventos

## Enlace a la fuente de los datos
https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=57be24206a91b510VgnVCM2000001f4a900aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default


## Procedimiento

- El proceso python se ha configurado en un cron de la máquina empleada para que ejecute diariamente todas las noches a las 22:00.

- El proceso carga en un dataframe la respuesta de la llamada al API con los datos, que los devuelve en formato CSV.

- Se realiza una limpieza de datos, se eliminan:
  - Aquellos registros que no tengan valor para las columnas 'HORA', 'LATITUD', 'LONGITUD', 'FECHA', 'FECHA-FIN'.
  - Aquellos registros cuya hora de evento comience a las '00:00'. Se ha observado que estos eventos, por su título, y público objetivo, no tiene sentido que comiencen tan tarde.

- Se hace un procesamiento de los eventos para detectar aquellos que vengan especificados como patrón, y generar un registro de evento, desde la fecha inicial, hasta la fecha final, a la hora y días de la semana correspondientes.

- Finalmente se configura la conexión de la base de datos, y se construyen las queries para las insercciones de los eventos resultantes.

## Consideraciones

- Como el proceso se ejecuta diariamente, es posible, que el evento venga repetido en los datos diarios. Para evitar duplicar eventos, se ha generado una clave única de fecha de evento y su localización. Se planteó inicialmente incluir el título del evento, pero se observó que el mismo evento, su título no venía escrito siempre de la misma forma, duplicándose.




