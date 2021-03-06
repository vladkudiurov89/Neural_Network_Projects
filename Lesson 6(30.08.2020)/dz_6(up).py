# -*- coding: utf-8 -*-
"""dz-6(UP).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LN5yNwgpYCa8XGkDp0_KL5MemvG--Fwo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation

import datetime as dt
import matplotlib.dates as mdates

# Подключаем Диск
from google.colab import drive
drive.mount('/content/drive')

# Загружаем данные
df = pd.read_csv('/content/drive/My Drive/datasets/date_csv/Google_Stock_Price_Train.csv', sep=',')
data = df.loc[:,["Open"]].values

# Подготовка данных
train = data[:len(data)-50] 
test = data[len(train):]
train=train.reshape(train.shape[0],1)

scaler = MinMaxScaler(feature_range= (0,1)) 
train_scaled = scaler.fit_transform(train) 

plt.plot(train_scaled)
plt.show()

# Формируем выборки
X_train = []
y_train = []
timesteps = 50

for i in range(timesteps, train_scaled.shape[0]):
    X_train.append(train_scaled[i-timesteps:i,0])
    y_train.append(train_scaled[i,0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)

inputs = data[len(data) - len(test) - timesteps:]
inputs = scaler.transform(inputs)

X_test = []
for i in range(timesteps, inputs.shape[0]):
    X_test.append(inputs[i-timesteps:i, 0])
X_test = np.array(X_test)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Создаём LSTM модель
model = Sequential()
model.add(LSTM(10, input_shape=(None,1)))
model.add(Dense(1))

model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train, y_train, epochs=15, batch_size=1)

predicted_data2=model.predict(X_test)
predicted_data2=scaler.inverse_transform(predicted_data2)

plt.figure(figsize=(8,4), dpi=80, facecolor='w', edgecolor='k')
plt.plot(test,color="LimeGreen",label="Real values")
plt.plot(predicted_data2,color="Gold",label="Predicted LSTM result")
plt.legend()
plt.xlabel("Days")
plt.ylabel("Values")
plt.grid(True)
plt.show()