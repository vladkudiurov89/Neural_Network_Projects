# -*- coding: utf-8 -*-
"""DZ-4(LIGHT).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I4tNmWbv3gLv9ZCMBHMLA9mm5VgNjTYB
"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import files # Для работы с файлами 
import numpy as np # Для работы с данными 
import pandas as pd # Для работы с таблицами
import matplotlib.pyplot as plt # Для вывода графиков
import os # Для работы с файлами
# %matplotlib inline

from tensorflow.keras import utils # Для работы с категориальными данными
from tensorflow.keras.models import Sequential # Полносвязная модель
from tensorflow.keras.layers import Dense, Dropout, SpatialDropout1D, BatchNormalization, Embedding, Flatten, Dropout, Conv1D# Слои для сети
from tensorflow.python.keras.optimizers import Adam, RMSprop
from tensorflow.keras.optimizers import Adam, Adadelta # Алгоритмы оптимизации, для настройки скорости обучения
from tensorflow.keras.preprocessing.text import Tokenizer # Методы для работы с текстами и преобразования их в последовательности
from tensorflow.keras.preprocessing.sequence import pad_sequences # Метод для работы с последовательностями

from sklearn.preprocessing import LabelEncoder # Метод кодирования тестовых лейблов
from sklearn.model_selection import train_test_split # Для разделения выборки на тестовую и обучающую
from google.colab import drive # Для работы с Google Drive
import time # Импортируем библиотеку time

import pandas as pd
import numpy as np

from google.colab import drive
drive.mount('/content/drive')

!unzip -q '/content/drive/My Drive/datasets/texts/Тексты писателей.zip' -d '/content/texts'

# Запускаем все необходимые функции

def readText(fileName): # Объявляем функции для чтения файла. На вход отправляем путь к файлу
  f = open(fileName, 'r')        # Задаем открытие нужного файла в режиме чтения
  text = f.read()                # Читаем текст
  text = text.replace("\n", " ") # Переносы строки переводим в пробелы
  
  return text                    # Возвращаем текст файла

className = ["О. Генри", "Стругацкие", "Булгаков", "Саймак", "Фрай", "Брэдберри"] # Объявляем интересующие нас классы
nClasses = len(className) # Считаем количество классов

# Формирование обучающей выборки по листу индексов слов
# (разделение на короткие векторы)
def getSetFromIndexes(wordIndexes, xLen, step): # функция принимает последовательность индексов, размер окна, шаг окна
  xSample = [] # Объявляем переменную для векторов
  wordsLen = len(wordIndexes) # Считаем количество слов
  index = 0 # Задаем начальный индекс 

  while (index + xLen <= wordsLen):# Идём по всей длине вектора индексов
    xSample.append(wordIndexes[index:index+xLen]) # "Откусываем" векторы длины xLen
    index += step # Смещаеммся вперёд на step
    
  return xSample

# Формирование обучающей и проверочной выборки
# Из двух листов индексов от двух классов
def createSetsMultiClasses(wordIndexes, xLen, step): # Функция принимает последовательность индексов, размер окна, шаг окна

  # Для каждого из 6 классов
  # Создаём обучающую/проверочную выборку из индексов
  nClasses = len(wordIndexes) # Задаем количество классов выборки
  classesXSamples = []        # Здесь будет список размером "кол-во классов*кол-во окон в тексте*длину окна (например, 6 по 1341*1000)"
  for wI in wordIndexes:      # Для каждого текста выборки из последовательности индексов
    classesXSamples.append(getSetFromIndexes(wI, xLen, step)) # Добавляем в список очередной текст индексов, разбитый на "кол-во окон*длину окна" 

  # Формируем один общий xSamples
  xSamples = [] # Здесь будет список размером "суммарное кол-во окон во всех текстах*длину окна (например, 15779*1000)"
  ySamples = [] # Здесь будет список размером "суммарное кол-во окон во всех текстах*вектор длиной 6"
  
  for t in range(nClasses): # В диапазоне кол-ва классов(6)
    xT = classesXSamples[t] # Берем очередной текст вида "кол-во окон в тексте*длину окна"(например, 1341*1000)
    for i in range(len(xT)): # И каждое его окно
      xSamples.append(xT[i]) # Добавляем в общий список выборки
      ySamples.append(utils.to_categorical(t, nClasses)) # Добавляем соответствующий вектор класса

  xSamples = np.array(xSamples) # Переводим в массив numpy для подачи в нейронку
  ySamples = np.array(ySamples) # Переводим в массив numpy для подачи в нейронку
  
  return (xSamples, ySamples) # Функция возвращает выборку и соответствующие векторы классов

# Создаем функцию подготовки данных
def creat_train_data(maxWordsCount = 15000, xLen = 1000, step = 100):
    tokenizer = Tokenizer(num_words=maxWordsCount)
    tokenizer.fit_on_texts(trainText) # "Скармливаем" наши тексты, т.е. даём в обработку методу, который соберет словарь частотности

    # Преобразовываем текст в последовательность индексов согласно частотному словарю
    trainWordIndexes = tokenizer.texts_to_sequences(trainText) # Обучающие тесты в индексы
    testWordIndexes = tokenizer.texts_to_sequences(testText)  # Проверочные тесты в индексы

    #Формируем обучающую и тестовую выборку
    xTrain, yTrain = createSetsMultiClasses(trainWordIndexes, xLen, step) #извлекаем обучающую выборку
    xTest, yTest = createSetsMultiClasses(testWordIndexes, xLen, step)    #извлекаем тестовую выборку

    # Преобразовываем полученные выборки из последовательности индексов в матрицы нулей и единиц по принципу Bag of Words
    xTrain01 = tokenizer.sequences_to_matrix(xTrain.tolist()) # Подаем xTrain в виде списка, чтобы метод успешно сработал
    xTest01 = tokenizer.sequences_to_matrix(xTest.tolist())   # Подаем xTest в виде списка, чтобы метод успешно сработал

    return xTrain, xTrain01, yTrain, xTest, xTest01, yTest

#Загружаем обучающие тексты

trainText = [] #Формируем обучающие тексты
testText = [] #Формируем тестовые тексты

#Формирование необходимо произвести следующим образом 
#Класс каждого i-ого эллемента в обучающей выборке должен соответствовать 
#классу каждого i-ого эллемента в тестовой выборке

for i in className: #Проходим по каждому классу
  for j in os.listdir('texts/'): #Проходим по каждому файлу в папке с текстами #
    if i in j: #Проверяем, содержит ли файл j в названии имя класса i
      
      if 'Обучающая' in j: #Если в имени найденного класса есть строка "Обучающая" 
        trainText.append(readText('texts/' + j)) #добавляем в обучающую выборку
        print(j, 'добавлен в обучающую выборку') #Выводим информацию
      if 'Тестовая' in j: #Если в имени найденного класса есть строка "Тестовая"
        testText.append(readText('texts/' + j)) #добавляем в обучающую выборку
        print(j, 'добавлен в тестовую выборку') #Выводим информацию
  print()

# Создаем функцию подготовки данных
def creat_train_data(maxWordsCount = 15000, xLen = 1000, step = 100):
    tokenizer = Tokenizer(num_words=maxWordsCount)
    tokenizer.fit_on_texts(trainText)

    # Преобразовываем текст в последовательность индексов согласно частотному словарю
    trainWordIndexes = tokenizer.texts_to_sequences(trainText)
    testWordIndexes = tokenizer.texts_to_sequences(testText)

    #Формируем обучающую и тестовую выборку
    xTrain, yTrain = createSetsMultiClasses(trainWordIndexes, xLen, step)
    xTest, yTest = createSetsMultiClasses(testWordIndexes, xLen, step)

    # Преобразовываем полученные выборки из последовательности индексов в матрицы нулей и единиц по принципу Bag of Words
    xTrain01 = tokenizer.sequences_to_matrix(xTrain.tolist())
    xTest01 = tokenizer.sequences_to_matrix(xTest.tolist())

    return xTrain, xTrain01, yTrain, xTest, xTest01, yTest

_, xTrain01, yTrain, _, xTest01, yTest = creat_train_data(maxWordsCount = 15000, xLen = 1000, step = 100)

def create_model():
  model = Sequential()
  model.add(Dense(200, input_dim=15000, activation="relu"))
  model.add(Dropout(0.25))
  model.add(BatchNormalization())
  model.add(Dense(6, activation='softmax'))
  model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
  return model

model = create_model()
model.summary()

#Обучаем сеть на выборке, сформированной по bag of words - xTrain01
history = model.fit(xTrain01, yTrain, epochs=10, batch_size=128, validation_data=(xTest01, yTest))

plt.plot(history.history['accuracy'], 
         label='Доля верных ответов на обучающем наборе')
plt.plot(history.history['val_accuracy'], 
         label='Доля верных ответов на проверочном наборе')
plt.xlabel('Эпоха обучения')
plt.ylabel('Доля верных ответов')
plt.legend()
plt.show()

data = [[1, 200, 'relu', 15000, None, round(history.history['val_accuracy'][-1], 3)]]
data

# чистим оперативную память
import gc    
gc.collect()

# 1
maxWordsCountList = [10,1000,10000,25000]
for i in maxWordsCountList:
    gc.collect()
    # Подготавливаем данные
    _, xTrain01, yTrain, _, xTest01, yTest = creat_train_data(maxWordsCount = i, xLen = 1000, step = 100)
    # Создаем сеть
    model01 = Sequential()
    model01.add(Dense(200, input_dim=i, activation="relu")) # Указываем входной размер 
    model01.add(Dropout(0.25))
    model01.add(BatchNormalization())
    model01.add(Dense(6, activation='softmax'))

    model01.compile(optimizer='adam', loss='categorical_crossentropy',  metrics=['accuracy']
    history = model01.fit(xTrain01, yTrain, epochs=10, batch_size=128, validation_data=(xTest01, yTest))
                      
    data = data + [[1, 200, 'relu', i, None, round(history.history['val_accuracy'][-1], 3)]]

# 2.1
_, xTrain01, yTrain, _, xTest01, yTest = creat_train_data(maxWordsCount = 20000, xLen = 1000, step = 100)
neurons_list = [10, 50, 100, 500, 1000, 2000]

for i in neurons_list:
    gc.collect()
    # Создаем сеть
    model01 = Sequential()
    model01.add(Dense(i, input_dim=20000, activation="relu"))
    model01.add(Dropout(0.25))
    model01.add(BatchNormalization())
    model01.add(Dense(6, activation='softmax'))

    model01.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    history = model01.fit(xTrain01, yTrain, epochs=10, batch_size=128, validation_data=(xTest01, yTest))
    data = data + [[1, i, 'relu', 20000, None, round(history.history['val_accuracy'][-1], 3)]]

# 2.2
for i in neurons_list:
    gc.collect()
    # Создаем сеть
    model01 = Sequential()
    model01.add(Dense(i, input_dim=20000, activation="relu"))
    model01.add(Dense(i, activation="relu"))               
    model01.add(Dropout(0.25))
    model01.add(BatchNormalization())
    model01.add(Dense(6, activation='softmax'))

    model01.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    history = model01.fit(xTrain01, yTrain, epochs=10, batch_size=128, validation_data=(xTest01, yTest))
    data = data + [[2, i, 'relu', 20000, None, round(history.history['val_accuracy'][-1], 3)]]

# 2.3

gc.collect()
model01 = Sequential()
model01.add(Dense(200, input_dim=20000, activation="linear"))
model01.add(Dropout(0.25))
model01.add(BatchNormalization())
model01.add(Dense(6, activation='softmax'))

model01.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
history = model01.fit(xTrain01, yTrain, epochs=10, batch_size=128, validation_data=(xTest01, yTest))
data = data + [[1, 200, 'linear', 20000, None, round(history.history['val_accuracy'][-1], 3)]]

df = pd.DataFrame(data, columns = ['Layers', 'Neurons', 'Activation','MaxWordCount', 'Emb_size', 'val_accuracy'])
df

# 3 
import gc
maxWordsCount = 50000
xLen = 1000
step = 100
xTrain, _, yTrain, xTest, _, yTest = creat_train_data(maxWordsCount=maxWordsCount, xLen=xLen, step=step)
data = []
emb_list = [10, 50 ,200]

for i in emb_list:
    gc.collect()
    modelE = Sequential()
    modelE.add(Embedding(50000, i, input_length=xLen))
    modelE.add(SpatialDropout1D(0.2))
    modelE.add(Flatten())
    modelE.add(BatchNormalization())
    modelE.add(Dense(200, activation="relu"))
    modelE.add(Dropout(0.2))
    modelE.add(BatchNormalization())
    modelE.add(Dense(6, activation='softmax'))

    modelE.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    history = modelE.fit(xTrain, yTrain, epochs=10, batch_size=128, validation_data=(xTest, yTest))
    data = data + [[1, 200, 'relu', 50000, i, round(history.history['val_accuracy'][-1], 3)]]

df = pd.DataFrame(data, columns = ['Layers', 'Neurons', 'Activation','MaxWordCount', 'Emb_size', 'val_accuracy'])
df