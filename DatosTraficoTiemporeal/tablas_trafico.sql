CREATE TABLE SensoresTrafico ( id INT NOT NULL , tipo_elem INT NOT NULL COMMENT '0 - Urbano 1 M-30' , distrito INT NOT NULL , cod_cent VARCHAR(10) NOT NULL , nombre VARCHAR(250) NOT NULL , longitud FLOAT NOT NULL , latitud FLOAT NOT NULL , utm_x FLOAT NOT NULL , utm_y FLOAT NOT NULL , PRIMARY KEY (id)) ENGINE = InnoDB;

CREATE TABLE DatosTrafico ( id INT NOT NULL AUTO_INCREMENT, id_sensor INT NOT NULL , fecha DATETIME NOT NULL , intensidad INT NOT NULL , ocupacion INT NOT NULL , carga INT NOT NULL , nivelServicio FLOAT NOT NULL , intensidadSat INT NOT NULL , error VARCHAR(1) NOT NULL , subarea INT NOT NULL , st_x FLOAT NOT NULL , st_y FLOAT NOT NULL , dia_semana INT NOT NULL , mes INT NOT NULL , hora INT NOT NULL , PRIMARY KEY (id), INDEX (id_sensor)) ENGINE = InnoDB;

CREATE TABLE CamarasSensores (
	id_camara INT NOT NULL,
	id_sensor INT NOT NULL,
	Distancia INT NOT NULL,
	CONSTRAINT CamarasSensores_PK PRIMARY KEY (id_camara,id_sensor)
)
ENGINE=InnoDB
DEFAULT CHARSET=latin1
COLLATE=latin1_swedish_ci;


ALTER TABLE proyecto.DatosTrafico ADD CONSTRAINT DatosTrafico_FK FOREIGN KEY (id_sensor) REFERENCES proyecto.SensoresTrafico(id);
