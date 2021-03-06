# -*- coding: utf-8 -*-
"""Generar Dataset.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wL0Cr3hes47xf9QLrKNa_3_0pd7tGI9n
"""

import pandas as pd
import numpy as np

df = pd.read_csv('cluster42.csv')

"""Cluster e index no me aportan nada"""

df.drop('cluster', axis=1, inplace=True)
df.drop('index', axis=1, inplace=True)

"""Fecha al principio y ordenado por fecha (esto lo oharé en la consulta SQL)"""

df.insert(0,'fecha', df.pop("fecha"))

df['fecha'] =  pd.to_datetime(df['fecha'])

df = df.sort_values(['fecha'], ascending=1)

"""Todos los campos del DF a números"""

df = df.apply(pd.to_numeric)

df.dtypes

"""Me cargo las columans que no me valen"""

df=df.drop(['fecha','num_cars_min', 'num_cars_max', 
            'num_cars_min_woo', 'num_cars_max_woo',
            'int_min', 'int_max', 'ocu_min', 'ocu_max', 
            'car_min', 'car_max', 'int_min_woo', 'int_max_woo', 
            'ocu_min_woo', 'ocu_max_woo', 
            'car_min_woo', 'car_max_woo'], axis=1)

df.columns

"""Para un primer entrenamiento, me quedo sólo con pocas coilumnas"""

df1 = df[[ 'ocu_mean','num_cars_mean','int_mean',
        'car_mean','dia_semana', 'dia_mes', 'festivo', 'eve_3h', 'gran_evento']]

"""Campo objetivo es OCU+1"""

df1['ocu+1']= df1.ocu_mean.shift(-1)

"""En Df1 tenemos lo que queremos entrenar...."""

df1.tail()

"""Quito la última fila..."""

df1 = df1.drop([1823])
df1.tail()

df1 = df1.fillna(0)

df1.head()

from sklearn.preprocessing import MinMaxScaler

values = df1.values
print(values.shape)

values = values.astype('float32')

scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)

scaled.shape

scaled.shape[0]

"""Aqui luego habrá que incluir los datos de los ultimos n medidas (series to supervised)"""

n_train = int(scaled.shape[0] * 0.75)

train = scaled[:n_train, :]
test = scaled[n_train:, :]
print(train.shape, test.shape)

train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]

# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

from matplotlib import pyplot

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# design network
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
# fit network
history = model.fit(train_X, train_y, epochs=50, batch_size=72, validation_data=(test_X, test_y), verbose=2, shuffle=False)
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

from math import sqrt
from numpy import concatenate
from sklearn.metrics import mean_squared_error

# make a prediction
yhat = model.predict(test_X)
test_X_1 = test_X.reshape((test_X.shape[0], test_X.shape[2]))

print(yhat.shape, test_X_1.shape)

# invert scaling for forecast
inv_yhat = concatenate((yhat, test_X_1), axis=1)

inv_yhat_1 = scaler.inverse_transform(inv_yhat)

inv_yhat_1 = inv_yhat_1[:,0]

inv_yhat_1.shape

test_y = test_y.reshape((len(test_y), 1))

inv_y = concatenate((test_y, test_X[:,0,:]), axis=1)

print (test_y.shape, test_X[:,0,:].shape, test_X[:, 1:].shape)

inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,0]
# calculate RMSE

rmse = sqrt(mean_squared_error(inv_y, inv_yhat_1))
print('Test RMSE: %.3f' % rmse)

df_y = pd.DataFrame(data=inv_y.tolist(), columns=['y'])

df_y['y_pred']=inv_yhat_1

df_y

pyplot.plot(inv_y, label='OCU')
pyplot.plot(inv_yhat_1, label='OCU PRED')
pyplot.legend()
pyplot.show()

"""# Ahora con todo"""



df1 = df

"""Campo objetivo es OCU+1"""

df1['ocu+1']= df1.ocu_mean.shift(-1)

"""En Df1 tenemos lo que queremos entrenar...."""

df1.tail()

"""Quito la última fila..."""

df1 = df1.drop([df1.shape[0]-1])
df1.tail()

df1=df1.replace(999999.0, np.nan)

df1 = df1.fillna(0)

df1.tail()

from sklearn.preprocessing import MinMaxScaler

values = df1.values
print(values.shape)

values = values.astype('float32')

scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)

scaled.shape

scaled.shape[0]

"""Aqui luego habrá que incluir los datos de los ultimos n medidas (series to supervised)"""

n_train = int(scaled.shape[0] * 0.75)

train = scaled[:n_train, :]
test = scaled[n_train:, :]
print(train.shape, test.shape)

train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]



# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

from matplotlib import pyplot



from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# design network
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
# fit network
history = model.fit(train_X, train_y, epochs=200, batch_size=72, validation_data=(test_X, test_y), verbose=2, shuffle=False)
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

from math import sqrt
from numpy import concatenate
from sklearn.metrics import mean_squared_error

# make a prediction
yhat = model.predict(test_X)
test_X_1 = test_X.reshape((test_X.shape[0], test_X.shape[2]))

print(yhat.shape, test_X_1.shape)

# invert scaling for forecast
inv_yhat = concatenate((yhat, test_X_1), axis=1)

inv_yhat_1 = scaler.inverse_transform(inv_yhat)

inv_yhat_1 = inv_yhat_1[:,0]

inv_yhat_1.shape

test_y = test_y.reshape((len(test_y), 1))

inv_y = concatenate((test_y, test_X[:,0,:]), axis=1)

print (test_y.shape, test_X[:,0,:].shape, test_X[:, 1:].shape)

inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,0]
# calculate RMSE

rmse = sqrt(mean_squared_error(inv_y, inv_yhat_1))
print('Test RMSE: %.3f' % rmse)

df_y = pd.DataFrame(data=inv_y.tolist(), columns=['y'])

df_y['y_pred']=inv_yhat_1

df_y

pyplot.plot(inv_y, label='OCU')
pyplot.plot(inv_yhat_1, label='OCU PRED')
pyplot.legend()
pyplot.show()





"""# Entrenando con menos datos, y guardandome otros para el final"""



df1 = df

"""Campo objetivo es OCU+1"""

df1['ocu+1']= df1.ocu_mean.shift(-1)

"""En Df1 tenemos lo que queremos entrenar...."""

df1.tail()

"""Quito la última fila..."""

df1 = df1.drop([df1.shape[0]-1])
df1.tail()

df1=df1.replace(999999.0, np.nan)

df1 = df1.fillna(0)

df1.tail()

from sklearn.preprocessing import MinMaxScaler

values = df1.values
print(values.shape)

values = values.astype('float32')

values

scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)

scaled

scaled.shape[0]

n_train = int(scaled.shape[0] * 0.65)
n_test = int(scaled.shape[0] * 0.25)
n_val = int(scaled.shape[0] * 0.10)

train = scaled[:n_train, :]
resto = scaled[n_train:, :]
test = resto[:n_test, :]
val = resto[n_test:,:]
print(train.shape, test.shape, val.shape)

val

train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
val_X, val_y = val[:, :-1], val[:, -1]

guarda_y = val_y
guarda_X = val_X

# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
val_X = val_X.reshape((val_X.shape[0],1,val_X.shape[1]))

guarda_X = val_X

print(train_X.shape, train_y.shape, test_X.shape, test_y.shape, val_X.shape, val_y.shape)

from matplotlib import pyplot



from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# design network
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
# fit network
history = model.fit(train_X, train_y, epochs=200, batch_size=72, validation_data=(test_X, test_y), verbose=2, shuffle=False)
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

from math import sqrt
from numpy import concatenate
from sklearn.metrics import mean_squared_error

guarda_y

# make a prediction
yhat = model.predict(guarda_X)
yhat

val_X_1 = guarda_X.reshape((guarda_X.shape[0], guarda_X.shape[2]))

print(guarda_X.shape, val_X_1.shape)

print(yhat.shape, val_X_1.shape)

# invert scaling for forecast
inv_yhat = concatenate((val_X_1, yhat), axis=1)

inv_yhat

inv_yhat_1 = scaler.inverse_transform(inv_yhat)
inv_yhat_1

inv_yhat_1 = inv_yhat_1[:, -1]

inv_yhat_1

inv_yhat_1.shape

val_y = val_y.reshape((len(val_y), 1))

inv_y = concatenate(( val_X[:,0,:], val_y), axis=1)

print (val_y.shape, val_X[:,0,:].shape, val_X[:, 1:].shape)

inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:, -1]
# calculate RMSE

rmse = sqrt(mean_squared_error(inv_y, inv_yhat_1))
print('Test RMSE: %.3f' % rmse)

df_y = pd.DataFrame(data=inv_y.tolist(), columns=['y'])

df_y['y_pred']=inv_yhat_1

df_y

pyplot.plot(inv_y, label='OCU')
pyplot.plot(inv_yhat_1, label='OCU PRED')
pyplot.legend()
pyplot.show()

















"""# Entrenar con más datos del pasado


https://machinelearningmastery.com/convert-time-series-supervised-learning-problem-python/


A partir de aqui basurilla.....
"""

def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    """
    Frame a time series as a supervised learning dataset.
    Arguments:
        data: Sequence of observations as a list or NumPy array.
        n_in: Number of lag observations as input (X).
                Observaciones para atras
        n_out: Number of observations as output (y).
                Observaciones para adelante +1 (es decir, si quiero ver t+1, hay que poner 2)
        dropnan: Boolean whether or not to drop rows with NaN values.
    Returns:
        Pandas DataFrame of series framed for supervised learning.
    """
    n_vars = 1 if type(data) is list else data.shape[1]
    nombre_col=list(data.columns) 
    print(nombre_col)
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [(nombre_col[j]+'(t-%d)' % (i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [(nombre_col[j]+'(t)') for j in range(n_vars)]
        else:
            names += [(nombre_col[j]+'(t+%d)' % (i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg

otro = series_to_supervised(df,3,2,dropnan=True)

otro.columns

cols = [c for c in otro.columns if c.lower()[-5:] != '(t+1)']

cols.append('ocu_mean(t+1)')

otro = otro[cols]

otro.insert(0,'ocu(t+1)', otro.pop("ocu_mean(t+1)"))

otro.corr()

from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

features = otro.columns.drop(['ocu(t+1)'])
X = otro[features].values
y = otro['ocu(t+1)'].values

train_size = int(len(X) * 0.80)
train_X, test_X = X[0:train_size], X[train_size:len(X)]

splits = TimeSeriesSplit(n_splits=5)
index = 1
for train_index, test_index in splits.split(X):
	train = X[train_index]
	test = X[test_index]
	print('Observations: %d' % (len(train) + len(test)))
	print('Training Observations: %d' % (len(train)))
	print('Testing Observations: %d' % (len(test)))

from matplotlib import pyplot

import numpy as np

class expanding_window(object):
    '''	
    Parameters 
    ----------
    
    Note that if you define a horizon that is too far, then subsequently the split will ignore horizon length 
    such that there is validation data left. This similar to Prof Rob hyndman's TsCv 
    
    
    initial: int
        initial train length 
    horizon: int 
        forecast horizon (forecast length). Default = 1
    period: int 
        length of train data to add each iteration 
    '''
    

    def __init__(self,initial= 1,horizon = 1,period = 1):
        self.initial = initial
        self.horizon = horizon 
        self.period = period 


    def split(self,data):
        '''
        Parameters 
        ----------
        
        Data: Training data 
        
        Returns 
        -------
        train_index ,test_index: 
            index for train and valid set similar to sklearn model selection
        '''
        self.data = data
        self.counter = 0 # for us to iterate and track later 


        data_length = data.shape[0] # rows 
        data_index = list(np.arange(data_length))
         
        output_train = []
        output_test = []
        # append initial 
        output_train.append(list(np.arange(self.initial)))
        progress = [x for x in data_index if x not in list(np.arange(self.initial)) ] # indexes left to append to train 
        output_test.append([x for x in data_index if x not in output_train[self.counter]][:self.horizon] )
        # clip initial indexes from progress since that is what we are left 
         
        while len(progress) != 0:
            temp = progress[:self.period]
            to_add = output_train[self.counter] + temp
            # update the train index 
            output_train.append(to_add)
            # increment counter 
            self.counter +=1 
            # then we update the test index 
            
            to_add_test = [x for x in data_index if x not in output_train[self.counter] ][:self.horizon]
            output_test.append(to_add_test)

            # update progress 
            progress = [x for x in data_index if x not in output_train[self.counter]]	
            
        # clip the last element of output_train and output_test
        output_train = output_train[:-1]
        output_test = output_test[:-1]
        
        # mimic sklearn output 
        index_output = [(train,test) for train,test in zip(output_train,output_test)]
        
        return index_output
        
        
#%%
#%%
# demo 

X = np.array([[1, 2], [3, 4], [1, 2], [3, 4], [1, 2], [3, 4]])

y = np.array([1, 2, 3, 4, 5, 6])
tscv = expanding_window()
for train_index, test_index in tscv.split(X):
    print(train_index)
    print(test_index)



X = np.random.randint(0,1000,size = (120,2))
y = np.random.randint(0,1000,size = (120,1))

tscv = expanding_window(initial = 36, horizon = 24,period = 1)
for train_index, test_index in tscv.split(X):
    print(train_index)
    print(test_index)

tscv = expanding_window(initial = 36, horizon = 24, period=1)
for train_index, test_index in tscv.split(X):
    print(train_index)
    print(test_index)

X.shape

from sklearn.linear_model import Lasso
from sklearn.ensemble import GradientBoostingRegressor

from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import numpy as np

model = GradientBoostingRegressor(random_state=0, 
                                           n_estimators=200, 
                                           max_features='sqrt')

Niterations = [500,1000]
learningRate = [1,0.5,0.1]
maxDepth = 3

param_search = {'n_estimators': Niterations,'learning_rate':learningRate }

tscv = TimeSeriesSplit(n_splits=5)
gsearch = GridSearchCV(estimator=model, cv=tscv,
                        param_grid=param_search, n_jobs=-1)
gsearch.fit(X, y)

model.get_params().keys()

print("best mean cross-validation score: {:.3f}".format(gsearch.best_score_))
print("best parameters: {}".format(gsearch.best_params_))

from sklearn.ensemble import RandomForestRegressor

maxDepth = range(1,20)
tuned_parameters = {'max_depth': maxDepth}

model = RandomForestRegressor(random_state=0, 
                                           n_estimators=200, 
                                           max_features='sqrt')

tscv = TimeSeriesSplit(n_splits=5)
gsearch = GridSearchCV(estimator=model, cv=tscv,
                        param_grid=tuned_parameters, n_jobs=-1)

gsearch.fit(X, y)

print("best mean cross-validation score: {:.3f}".format(gsearch.best_score_))
print("best parameters: {}".format(gsearch.best_params_))

