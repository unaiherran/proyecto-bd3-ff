USE proyecto;

DROP TABLE IF EXISTS CamarasTrafico;
DROP TABLE IF EXISTS ImagenesCamarasTrafico;

CREATE TABLE CamarasTrafico(
        id_camara INT(10) UNSIGNED PRIMARY KEY,
        feed VARCHAR(2083),
        longitud DECIMAL(11, 8),
        latitud DECIMAL(10, 8),
        video bool,
        foto bool
);

CREATE TABLE ImagenesCamarasTrafico(
        id_imagen INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        id_camara int(10) unsigned,
        imagen varchar(255),
        response text,
        num_cars int(10),
        fecha datetime
);

alter table ImagenesCamarasTrafico add index fk_camaras_imagenes_idx (ID_camara asc);
alter table ImagenesCamarasTrafico add constraint fk_camaras_imagenes foreign key(id_camara)
	references CamarasTrafico(id_camara);