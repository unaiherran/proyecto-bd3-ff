use proyecto;

## Separa los datos leidos en grouped_data en train y test
## Con train generaremos los modelos y las nuevas lecturas una vez esten entreados los modelos iran a test 
drop table if exists 0_train_data;
drop table if exists 0_test_data;


CREATE TABLE 0_train_data SELECT * FROM grouped_data_0 where fecha < '2019-11-17 23:59:59';

CREATE TABLE 0_test_data SELECT * FROM grouped_data_0 where fecha >= '2019-11-18 00:00:00';
