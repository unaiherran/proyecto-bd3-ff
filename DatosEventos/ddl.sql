DROP TABLE IF EXISTS DatosEventos;
CREATE TABLE DatosEventos (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,  
  fecha DATETIME NOT NULL,
  gratuito INT NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  longitud DECIMAL(11,8) NOT NULL,
  latitud DECIMAL(10,8) NOT NULL,
  cluster INT UNSIGNED NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- INSERT INTO DatosEventos(fecha, gratuito, titulo, longitud, latitud, cluster) VALUES ('2019-10-25 11:00:00', 0, "Circuit des Yeux's", -3.651841641389484, 40.42342659084215, 7);

ALTER TABLE DatosEventos ADD CONSTRAINT fk_eve_clu FOREIGN KEY (cluster) REFERENCES Cluster(id_cluster);
ALTER TABLE DatosEventos ADD INDEX fk_eve_clu_idx (cluster ASC);

CREATE UNIQUE INDEX eve_unique_idx ON DatosEventos(fecha, cluster);