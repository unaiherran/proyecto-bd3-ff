use proyecto;

SELECT num_cars
, clu.id_cluster
, cam.id_camara
, ima.fecha

from ImagenesCamarasTrafico ima
INNER JOIN CamarasTrafico cam
ON ima.id_camara = cam.id_camara

inner join Cluster clu
on cam.Cluster = clu.id_cluster
#order by fecha

where (ima.fecha BETWEEN str_to_date('2019-10-01 23:35', '%Y-%m-%d %H:%i') 
	AND str_to_date('2019-10-21 23:50', '%Y-%m-%d %H:%i')) and (clu.id_cluster = 1)
;
