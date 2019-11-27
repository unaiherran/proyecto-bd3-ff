# Crawler de camaras del Ayuntamiento de Madrid

El crawler se realiza en varios pasos. Primero tenemos que dar forma a
los datos que hemos obtenido del Ayuntamiento, el fichero `CCTV.kml` y
obtener el listado de las camaras, así como la URL de la que descargar
sus imagenes de una forma más amigable. Para eso usamos
`sacar_listado.py` que convierete dicho `kml` en
`lista_camaras.csv`

Una vez obtenido este csv tenemos dos procesos distintos. 

Uno, `poblar_base_datos_camaras.py`, que se encarga de introducir esos
datos en la base de datos.

Y luego tenemos `scrap_camara.py`, que es el scrapper en si mismo, que
se conecta a la url suministrada y baja la última imagen de cada camara
y la guarda en el directorio `scrapped/`

# Almacenar en S3 - Amazon Rekognition – AWS
`send_to_s3.py` hace varias cosas. 

Por un lado almacena la imagen en S3, para poder recuperarla luego.

Tambien comprueba si esa imgen ha sido ya procesada. Puede que la
lectura del feed nos de la misma imagen que en el ultimo crawl, y no
queremos duplicar ni la imagen ni la información que sacamos de ella.
Para ello hace distintas comprobaciones del tamaño, el hash de los
primeros bytes del archivo y finalmente el hash completo del archivo.
Esto se realiza así para darle menos trabajo al servidor que va a
realizar las comprobaciones, ya que calcular hashes de archivos es
bastante caro computacionalmente hablando.

Por último, y quizá el paso más importante es el mandar esa imagen a
Amazon Rekognition, un servicio web de AWS que realiza un analisis de
segmentación de imagen y devuelve todos los objetos que se 'ven' en la
imagen. Esa información es limpiada un poco y se almacena en nuestra
base de datos como el número de coches que se ven en la imagen.
