# Documentación

## Objetivo
El objetivo principal en este módulo es la extracción de datos metereológicos de la Provincia de Madríd procedentes de la pagina de Aemet

## Librerías
Para el manejo de la base de datos empleo el ORM sqlalchemy que permite interactuar con la base de datos como si fuesen objetos
mientras que para el manejo de los datos empleo pandas

## DOC
El scrip para obtener los datos de la AEMET consta de una clase donde se encuentran implementados los métodos necearios para extraer los datos metereológicos y guardarlos en la base de datos. Puesto que los datos de la pagina se actualizan cada hora este script se ejecuta cada hora para grabar los datos recientes en la base.



