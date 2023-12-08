# Чтение csv датасета и Вывод параметров датасета

import os
import pandas
from datetime import datetime

now = datetime.now()

dataset_csv='dataset.csv'
df = pandas.read_csv(dataset_csv, delimiter=',')#, index_col='file_name')
print(df.columns.tolist())
print("Всего записей = ", len(df))
print("Уникальных классов = ", len(df['class'].unique()))
print(df['class'].value_counts())

print("\n")
pandas.set_option('display.max_rows', None)
print(df['class'].value_counts())


print("time =", datetime.now()-now)

#print(df.info())

### Пример: выбрать n треков класса 'bigtown' случайным образом
##n = 3
##class_noise = 'bigtown'
##print(df[df['class'].isin([class_noise])].sample(n)[['file_name', 'class']])
##
### Еще пример
##print(df[df['class'] =='instrumental'].sample(n)[['file_name', 'class']])


