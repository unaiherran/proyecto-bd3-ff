# Datos de tráfico en tiempo real

La obtención de los datos de tráfico en tiempo real se realiza en dos pasos:

## Descarga del xml del ayuntamiento de Madrid

El ayuntamiento de madrid provee de un API con un endpoint que ofrece los datos recopilados de los sensores de tráfico que tiene repartidos por toda la ciudad. 
La direción del endpoint es http://informo.munimadrid.es/informo/tmadrid/pm.xml y los datos se actualizan con una periocidad aproximada de 5 minutos. 
Cada actualización de los datos retorna mas de 4.000 registros.
