# -*- coding: utf-8 -*-
"""DZ-17(Light).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xdGxWuQgQbj32lXYXHZKJ7888ioGOmpg
"""

# Commented out IPython magic to ensure Python compatibility.
# Статический вывод графики (графики отображаются в той ячейке, в которой используется plt.show())
# %matplotlib inline
from sklearn.preprocessing import StandardScaler, LabelEncoder # Импортируем библиотеку StandardScaler и LabelEncoder
from sklearn.cluster import KMeans # Импортируем библиотуке KMeans для кластеризации
from sklearn.metrics.cluster import homogeneity_score
from sklearn.manifold import TSNE
import time
import os
import pandas as pd # импортируем библиотеку обработки и анализа данных pandas
import matplotlib.pyplot as plt # Импортируем модуль pyplot библиотеки matplotlib для построения графиков
from tensorflow.keras import utils # Импортируем модуль utils библиотеки tensorflow.keras для получения OHE-представления
import numpy as np # Импортируем библиотеку numpy
from keras.preprocessing.text import Tokenizer, text_to_word_sequence,tokenizer_from_json 
from tensorflow.keras.models import Sequential, Model # Полносвязная модель
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Reshape, Conv2DTranspose, Dropout, SpatialDropout1D, BatchNormalization, Embedding, Flatten, Activation # Слои для сети
from tensorflow.keras.preprocessing.sequence import pad_sequences # Метод для работы с последовательностями
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.datasets import mnist

# Подключаем диск
from google.colab import drive
drive.mount('/content/drive')

# Читаем данные из загруженной базы
df = pd.read_csv('/content/drive/My Drive/datasets/cluster/online_carts.csv') 
df.head()

# Удалим первый столбец и переименнуем его
new = df.drop(['Unnamed: 0'], axis =1)
new.insert(0, column='Дата', value = [x for x in range(len(new))]) 
new = new.fillna('unknown') 
new.head()

# Здесь будут лежать все индексы строк, где есть информация в формате даты
date_list = list(new[new['Валовая прибыль'].str.contains("\d\d.\d\d.2019")].index) 

indx=0
for i in range(len(new)):                       # Проходимся по каждой строке базы
  if i in date_list:                            # Если индекс находится среди тех, где есть формат даты
    indx = i                                    # Обновляем текущий индекс
  new['Дата'][i] = new['Валовая прибыль'][indx] # Присваиваем текущий индекс всем последующим строкам, пока не наткнемся на новый индекс-дату

new = new.drop(new[new['Дата'].str.contains('Период')].index,axis = 0)           # Удалим строки "Период"
new = new.drop(new[new['Валовая прибыль'].str.contains('unknown')].index,axis=0) # Удалим пустые строки между корзинами
new = new.drop(new[new['Валовая прибыль']==new['Дата']].index)                   # Удалим строки-даты, которые находятся в столбце корзин
new.reset_index(inplace=True)                                                    # Обновим индекс
new = new.drop('index',axis=1)                                                   # Удалим ненужную колонку
new.head()

new = new.drop(new[new['Дата'].str.contains('Период')].index,axis = 0)           # Выкинем превьюшные строки
new = new.drop(new[new['Валовая прибыль'].str.contains('unknown')].index,axis=0) # Выкинем пустые строки между корзинами
new = new.drop(new[new['Валовая прибыль']==new['Дата']].index)                   # Выкинем строки-даты, которые находятся в столбце корзин
new.reset_index(inplace=True)                                                    # Обновим индекс
new = new.drop('index',axis=1)                                                   # Выкинем ненужную, образовавшуюся после предыдущей операции колонку

cart_list = list(new[new['Валовая прибыль'].str.contains("MCOSM")].index)        # Здесь будут лежать все индексы строк, где строка содержит флаг начала корзины
cafre_list = list(new[new['Валовая прибыль'].str.contains("CAFRE")].index)       # Здесь будут лежать все индексы строк, где строка содержит флаг CAFRE

new.head(10)

carts = []                     # Здесь будут лежать все корзины 
cart=[]                        # В этом списке будет текущая корзина
i=0                            # Счетчик для прохождения по базе
val = new['Валовая прибыль']   # Будем работать с этим столбцом
allPositions = []              # Создаем пустой список позиций

while i!=len(new):             # Пока не дойдем до конца списка
  if i in cart_list:           # Если счетчик в списке индексов-корзин
    if i!=cart_list[-1]:       # Проверяем, если это не последний индекс-флаг
      ind = cart_list.index(i) # Текущему индексу-флагу присваиваем значение конкретно этой корзины
      # Пробегаемся дальше по счетчику до момента, когда он не будет равен следующему в списке индексу-флагу
      # Если условия соблюдаются, то закидываем следующую строку в текущую корзину
      # Инкремент счетчика
      while i<cart_list[ind+1]-1:
        cart.append(val[i+1])
        allPositions.append(val[i+1]) 
        i+=1     
    else:                      # Если же текущий индекс-флаг последний в спискf
      # Пробегаемся дальше по счетчику до момента, когда он не будет равен концу списка всех строк в столбце-1
      # Если условия соблюдаются, то закидываем следующую строку в текущую корзину
      # Инкремент счетчика
      while i<(len(new)-1):
        cart.append(val[i+1])
        allPositions.append(val[i+1]) 
        i+=1
    carts.append(cart)         # Закидываем корзину в список всех корзин
    cart=[]                    # Очищаем корзину
  else:
    i+=1                       # Если счетчик не в списке корзин, то инкрементируем

len(carts)

items = 0
for cart in carts:
    for item in cart:
        items += 1
print(items)

print(len(carts)==len(cart_list))   # Проверка, если у нас количество корзин совпадает с количеством флагов корзин
print('Количество всех позиций: ', len(allPositions)) 
print('Пример того, что лежит в корзине: ', carts[0])

for i in range(10):
    print(carts[i])

# Отобразим гистограмму размеров корзин
plt.hist([len(c) for c in carts], 20, [1, 21])
plt.show()

allPositions[:10]

labelEncoder = LabelEncoder()  # Создаем объект LabelEncoder 
labelEncoder.fit(allPositions) # Обрабатываем все имеющиеся позиции товаров

maxPositionsCount = max(labelEncoder.transform(allPositions))+1 # Посчитаем количество уникальных товаров
print(maxPositionsCount)

cartsIndexes = [labelEncoder.transform(c) for c in carts] # Создаем список индексов для каждой корзины

n = 0                  # Укажем номер корзины
print(carts[n])        # Отобразим содержимое этой корзины
print(cartsIndexes[n]) # Отобразим соответствующие индексы

'''
  Функция преобразования вектора по приницпу bag of words
    Входные параметры:
      - trainVector - исходный вектор индексов слов
      - wordsCount - установленная длинна вектора
    Функция возращает: 
      - сформированный вектор из 0 и 1
'''
def changeXTo01(trainVector, wordsCount):
  out = np.zeros(wordsCount)                   # Создаем вектор из нулей длинной wordsCount
  for x in trainVector:                        # Пробегаем по всем индексам в trainVector
    out[x] = 1                                 # Изменяем на 1 значение out в позиции текущего индекса 
  return out                                   # Возвращаем сформированный вектор


'''
  Функция преобразования выборки (обучающей или проверочной) по принципе Bag of words
    Входные параметры:
      - trainSet - выборка
      - wordsCount - установленная длинна вектора
    Функция возращает: 
      - сформированная выборка из 0 и 1
'''
def changeSetTo01(trainSet, wordsCount):
  out = []                                     # Создаем пустой список  
  for x in trainSet:                           # Пробегаем по всем элемента выборки
    out.append(changeXTo01(x, wordsCount))     # Получаем вектор Bag of words для текущего элемента    
  return np.array(out)                         # Возрващаем сформированную выборку

carts01 = changeSetTo01(cartsIndexes, maxPositionsCount) # Создаем выборку по принципу bag of words

print(carts[n])        # Выводим содержимое корзины
print(cartsIndexes[n]) # Выводим список соответствующих индексов
print(carts01[n])      # Выводим соответсвующий список bag of words

# Commented out IPython magic to ensure Python compatibility.
# %%time
# cur_time = time.time()
# clustersCount = 8                                  # Указываем количество кластеров
# kmean = KMeans(clustersCount)                        # Создаем объект KMeans
# kmean.fit(carts01)                                   # Производим кластеризацию набора carts01
# labels = kmean.labels_                               # Сохраняем метки в переменную labels
# 
# npCarts = np.array(carts)                            # Преобразуем список корзин в numpy
# print('Время обработки: ', round(time.time() - cur_time,2),'c')

print(labels)                                                   # Отображаем метки кластеров
clusterSize = [sum(labels==i) for i in range(0, clustersCount)] # Создадим список размеров каждого кластера

# Выведем номер кластера и его размер
for i, s in enumerate(clusterSize):
  print(i, s)

def getCluster(x):
  clasterSize = x.shape[0]                           # Берем размер кластера
  sumX = np.sum(x, axis=0)                           # Считаем сумму кластера по позициям
  sumX /= clasterSize                                # Смотрим насколько часто конкретная позиция появляется в данном кластере
  
  positions = []                                     # Создаем пустой список позиций
  positionValues = []                                # Создаем пустой список значений
  
  for i in range(sumX.shape[0]):                     # Пробегаем по всем имеющимся примерам товаров
    if (sumX[i] > 0):                                # Если товар присутствует в данном кластере
      position = labelEncoder.inverse_transform([i]) # Получаем обратный энкодер
      positions.append(position)                     # Добавляем позицию в список позиций 
      positionValues.append(sumX[i])                 # В списк значений добавляем количество данной позиции в текущем кластере
  
  return positions, positionValues                   # Возвращаем список позиций кластера и количество каждой позиции

for clusterNumber in range(len(clusterSize)):                # Пробегаем по всем кластерам
  if (clusterSize[clusterNumber] > 5):                       # Если размер кластера больше 5
    pos, posVal = getCluster(carts01[labels==clusterNumber]) # Получаем позиции и их количество в текущем кластере
    print("Покупок:", clusterSize[clusterNumber])            # Выводим размер текущего кластера
    print("Позиций:", len(pos))                              # Выводим общее число позиций в текущем кластере
    pos = np.array(pos)                                      # Преобразуем в numpy
    posVal = np.array(posVal)                                # Преобразуем в numpy
    indexes = posVal > 0.6                                   # Берем индексы тех позиций, доля которых составляет больше 20%
    indexedPos = pos[indexes]                                # Выбираем эти позиции из pos
    indexedPosVal = posVal[indexes]                          # Выбираем доли этих позиций

    # Отображаем долю позиции и название самой позиции
    for i in range(len(indexedPos)):
      print(round(100*indexedPosVal[i]), "% ", indexedPos[i], sep="")

    print()
    print()

# Commented out IPython magic to ensure Python compatibility.
# %%time
# cost = []
# for i in range(1,15):
#   kmean = KMeans(i*1) # *20
#   kmean.fit(carts01)
#   cost.append(kmean.inertia_)
#   print("Готово разбиение на ", i*1, " классов", sep="")
#     
# plt.plot(cost, 'bx-')

max(labels)

# Разбиение на 280 классов
for clusterNumber in range(max(labels)):                     # Пробегаем по всем значениям
    if (clusterSize[clusterNumber] > 5):                     # Если размер кластера больше 5
      pos, posVal = getCluster(carts01[labels==clusterNumber]) # Получаем позиции и их количество в текущем кластере
      print("Покупок:", clusterSize[clusterNumber])            # Выводим размер текущего кластера
      print("Позиций:", len(pos))                              # Выводим общее число позиций в текущем кластере
      pos = np.array(pos)                                      # Преобразуем в numpy
      posVal = np.array(posVal)                                # Преобразуем в numpy
      indexes = posVal > 0.2                                   # Берем индексы тех позиций, доля которых составляет больше 20%
      indexedPos = pos[indexes]                                # Выбираем эти позиции из pos
      indexedPosVal = posVal[indexes]                          # Выбираем доли этих позиций

      # Отображаем долю позиции и название самой позиции
      for i in range(len(indexedPos)):
        print(round(100*indexedPosVal[i]), "% ", indexedPos[i], sep="")

      print()
      print()

carts_ = [[item for item in cart if not item.startswith('Услуга доставки')] for cart in carts]
len(carts_) # новый список содержит корзины, из которых удалены доставки

# Число позиций после удаления доставок:
items = 0
for cart in carts_:
    for item in cart:
        items += 1
print(items)

# Пересоздадим списки cartsIndexes and carts01:
carts, carts_ = carts_, carts # теперь в carts_ будут корзины с доставками
cartsIndexes = [labelEncoder.transform(c) for c in carts] 
carts01 = changeSetTo01(cartsIndexes, maxPositionsCount)

n = 0                  # Указываем номер корзины
print(carts[n])        # Выводим содержимое корзины
print(cartsIndexes[n]) # Выводим список соответствующих индексов
print(carts01[n])      # Выводим соответсвующий список bag of words

# Commented out IPython magic to ensure Python compatibility.
# # Выведите две гистограммы
# # Распределения размеров классов - сколько корзин
# # Распределение количества уникальных позиций в классе
# # Кластеризуем по-новой (мы изменили carts01)
# 
# %%time
# cost = []
# for i in range(1, 13):
#   kmean = KMeans(i) # *20
#   kmean.fit(carts01)
#   cost.append(kmean.inertia_)
#   print("Готово разбиение на ", i, " классов", sep="")
#     
# plt.plot(list(range(1, 13)), cost, 'bx-')

# Commented out IPython magic to ensure Python compatibility.
# %%time
# clustersCount = 9                                   # Указываем количество кластеров
# kmean = KMeans(clustersCount)                        # Создаем объект KMeans
# kmean.fit(carts01)                                   # Производим кластеризацию набора carts01
# labels = kmean.labels_                               # Сохраняем метки в переменную labels
# 
# npCarts = np.array(carts)
# len(carts), len(carts01)

print(labels)                                                   # Отображаем метки кластеров
clusterSize = [sum(labels==i) for i in range(0, clustersCount)] # Создадим список размеров каждого кластера

# Выведем номер кластера и его размер
for i, s in enumerate(clusterSize):
    print(i, s)

_ = plt.hist(labels, clustersCount, [0, clustersCount])

def printSize(cluster):
    """
    cluster: список корзин (в любом формате) 
    """
    print("Cluster has %d carts" % len(cluster))

n = 2 # номер класса
cluster = [cartsIndexes[i] for i in range(len(carts)) if labels[i] == n]
items = []
for i in cluster:
    items.extend(i)
print("Cluster #%d has %d carts" % (n , len(cluster)))

def printNumberUniqPositions(cluster):
    items = []
    for cart in cluster:
        items.extend(cart)
    uniqs = set()
    [uniqs.add(item) for item in items]
    print("Uniq positions:", len(uniqs))

printNumberUniqPositions(cluster)

def printPopularPositions(cluster, level=0.2):
    N = int(level*len(cluster)) 
    items = []
    for cart in cluster:
        items.extend(cart)
    uniqs = set()
    [uniqs.add(item) for item in items]
    qty = {id: 0 for id in uniqs} # словарь id -> в скольких корзинах встречается позиция id
    for cart in cluster:
        for id in cart:
            qty[id] += 1
    ids20 = [id for id in uniqs if qty[id] > N] # список ids которые встретились более чем в N корзинах
    print('Позиции, которые есть минимум в %d%% корзин:' % int(100*level), ids20)

printPopularPositions(cluster, level=0.2)

printPopularPositions(cluster, level=0.02)

printPopularPositions(cluster, level=0.01)

maxWordsCount = 10000
tok = Tokenizer(num_words=maxWordsCount, filters='!"#$%&()*+,-–—./:;<=>?@[\\]^_`{|}~\t\n\xa0', lower=True, split=' ', oov_token='unknown', char_level=False)
positions = []
for p in carts:
    positions.extend(p)
tok.fit_on_texts(positions)         
items = list(tok.word_index.items())

positionIds = tok.texts_to_sequences(positions)
positionIds[:10]

uniqPositions = set()
[uniqPositions.add(p) for p in positions]
print("Distinct positions:", len(uniqPositions))

def printPopularWords(cluster, level=0.2):
    pos_count = 0
    for cart in cluster:
        pos_count += len(cart) # Находим полное число позиций в кластере
    N = int(level*pos_count) # Пороговое количество позиций для слова.
    qty = {id: 0 for id in range(1, len(tok.word_index.items())+1)} # словарь id -> в скольких позициях встречается слово id
    for item in positionIds:
        for id in item:
            qty[id] += 1
    ids20 = [id for id in range(1, len(tok.word_index.items())+1) if qty[id] > N] # список ids слов, которые встретились более чем в N позициях
    words = [tok.index_word[id] for id in ids20]
    print('слова, которые есть минимум в %d%% позиций:' % int(100*level), words)

printPopularWords(cluster, level=0.2)

# Искомая продвинутая функция
def printAdvanced(cluster):
    printSize(cluster)
    printNumberUniqPositions(cluster)
    printPopularPositions(cluster)
    printPopularWords(cluster)

printAdvanced(cluster)