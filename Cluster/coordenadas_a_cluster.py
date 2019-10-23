import pickle
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd


def crear_modelo(filename):
    camaras = pd.read_csv("CoordCamaras.csv", sep=",")
    sensores = pd.read_csv("CoordSensores.csv", sep=",")
    sensores['tipo'] = 0
    camaras['tipo'] = 1
    camaras.columns = ['id', 'longitud', 'latitud', 'tipo']
    todo = pd.concat([camaras, sensores], sort=False)

    X_todo = todo.drop(columns=['id', 'tipo']).values

    num_cluster = 200
    random_state = 42

    kmeans = KMeans(n_clusters=num_cluster, random_state=random_state)

    kmeans.fit(X=X_todo)

    pickle_out = open(filename, "wb")
    pickle.dump(kmeans, pickle_out)
    pickle_out.close()


def load_model(filename="kmeans.21.3.joblib"):
    # Abrir el fichero con la descripcion del modelo
    file = open(filename, 'rb')

    # dump information to that file
    modelo = pickle.load(file)

    # close the file
    file.close()
    return modelo


def coordenadas_a_cluster(longitud, latitud, modelo):
    # longitud y latitud son float con las coordenadas del punto que quieres clusterizar
    # modelo es el modelo que cargamos al usar load_model

    coordenadas = np.array([longitud, latitud])
    return modelo.predict(X=coordenadas.reshape(1, -1))[0]


def main():
    # Uso:
    # cargar el modelo con load_model
    # coordenadas_a_cluster(longitud, latitud, modelo) devuelve el cluster al que pertenece esas coordenadas

    # Ejemplo:
    longitud = -3.89051645
    latitud = 40.42566934

    # cargamos el modelo
    modelo = load_model("kmeans.21.3.joblib")

    # realizamos la llamada
    print(coordenadas_a_cluster(longitud,latitud, modelo))


if __name__ == '__main__':
    main()