# -*- coding: utf-8 -*-
"""DZ-8(Ultro).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1io8VSK1XtLLjIPFPWA0qP5B7e3LVUrag
"""

# Commented out IPython magic to ensure Python compatibility.
#Подключаем библиотеки
from tensorflow.keras.optimizers import Adam, Adadelta
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import concatenate, Input, Dense, Dropout, BatchNormalization, Flatten, Conv1D, Conv2D, LSTM
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.keras.layers import MaxPooling2D, GlobalMaxPooling2D, MaxPooling1D
from keras.utils import plot_model
from google.colab import files
from keras.utils import to_categorical
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
# %matplotlib inline

from keras.utils import plot_model
import warnings
warnings.filterwarnings('ignore')

from google.colab import drive
drive.mount('/content/drive')

# Указываем путь к базе
data_path = '/content/drive/My Drive/datasets/data/'
!ls drive/MyDrive/datasets/data/bed/

# Функция для загрузки данных
def get_labels(path=data_path):
    labels = os.listdir(path)
    label_indices = np.arange(0, len(labels))
    return labels, label_indices, to_categorical(label_indices)

def wav2mfcc(file_path, max_len=11):
    wave, sr = librosa.load(file_path, mono=True, sr=None)
    wave = wave[::3]
    mfcc = librosa.feature.mfcc(wave, sr=16000)
    if (max_len > mfcc.shape[1]):
        pad_width = max_len - mfcc.shape[1]
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :max_len]   
    return mfcc

# Сохраняем данные в массив
def save_data_to_array(path=data_path, max_len=11):
    labels, _, _ = get_labels(path)
    for label in labels:
        mfcc_vectors = []
        wavfiles = [path + label + '/' + wavfile for wavfile in os.listdir(path + '/' + label)]
        for wavfile in tqdm(wavfiles, "Saving vectors of label - '{}'".format(label)):
            mfcc = wav2mfcc(wavfile, max_len=max_len)
            mfcc_vectors.append(mfcc)
        np.save(label + '.npy', mfcc_vectors)

# Функция получения выборки
def get_train_test(split_ratio=0.6, random_state=42):
    labels, indices, _ = get_labels(data_path)
    X = np.load(labels[0] + '.npy')
    y = np.zeros(X.shape[0])
    for i, label in enumerate(labels[1:]):
        x = np.load(label + '.npy')
        X = np.vstack((X, x))
        y = np.append(y, np.full(x.shape[0], fill_value= (i + 1)))
    assert X.shape[0] == len(y)
    return train_test_split(X, y, test_size= (1 - split_ratio), random_state=random_state, shuffle=True)

# Функция подготовки данных
def prepare_dataset(path=data_path):
    labels, _, _ = get_labels(path)
    data = {}
    for label in labels:
        data[label] = {}
        data[label]['path'] = [path  + label + '/' + wavfile for wavfile in os.listdir(path + '/' + label)]
        vectors = []
        for wavfile in data[label]['path']:
            wave, sr = librosa.load(wavfile, mono=True, sr=None)
            wave = wave[::3]
            mfcc = librosa.feature.mfcc(wave, sr=16000)
            vectors.append(mfcc)
        data[label]['mfcc'] = vectors
    return data

# Загружаем датасет
def load_dataset(path=data_path):
    data = prepare_dataset(path)
    dataset = []
    for key in data:
        for mfcc in data[key]['mfcc']:
            dataset.append((key, mfcc))
    return dataset[:100]

feature_dim_2 = 11
save_data_to_array(max_len=feature_dim_2)
# Загружаем данные
X_train, X_test, y_train, y_test = get_train_test()

feature_dim_1 = 20
channel = 1
num_classes = 3

# Подготавливаем X_train
X_train = X_train.reshape(X_train.shape[0], feature_dim_1, feature_dim_2, channel)
X_test = X_test.reshape(X_test.shape[0], feature_dim_1, feature_dim_2, channel)

# Подготавливаем Y_train
y_train_hot = to_categorical(y_train)
y_test_hot = to_categorical(y_test)

plt.imshow(X_train[100, :, :, 0])
print(y_train_hot[100])

# Создаём сеть
model = Sequential()
model.add(Flatten(input_shape=(feature_dim_1, feature_dim_2)))
model.add(Dense(64, activation='sigmoid'))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=['accuracy'])
                  
plot_model(model, to_file='model.png')

# Обучаем модель
history = model.fit(X_train, y_train_hot, batch_size=100, epochs=150, verbose=1, validation_data=(X_test, y_test_hot))
plt.plot(history.history['accuracy'], 
         label='Доля верных ответов на обучающем наборе')
plt.plot(history.history['val_accuracy'], 
         label='Доля верных ответов на проверочном наборе')
plt.xlabel('Эпоха обучения')
plt.ylabel('Доля верных ответов')
plt.legend()
plt.show()

# Функция прогнозирования
def predict(filepath, model):
    sample = wav2mfcc(filepath)
    sample_reshaped = sample.reshape(1, feature_dim_1, feature_dim_2, channel)
    return get_labels()[0][np.argmax(model.predict(sample_reshaped))]

# Результат модели
print(predict('/content/drive/My Drive/datasets/data/bed/52e228e9_nohash_0.wav', model=model))

