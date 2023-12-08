# Генерация датасета из файлов расположенных в папке sources

import numpy as np
import librosa
import soundfile as sf
import scipy.io.wavfile
from scipy import signal
import os, fnmatch
import csv

# Поиск всех wav-файлов в каталоге directory
def find_files(directory, pattern=['*.wav', '*.WAV']):
    '''find files in the directory'''

    files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern[0]):
            files.append(os.path.join(root, filename))

    return files

# Конвертация wav-файлов к 8кГц 16бит моно
def downsampling(source_files):
    '''Your new sampling rate'''

    new_rate = 8000

    for file in source_files:
            print("downsampling file = ", file)

            data, samplerate = sf.read(file)
            sf.write(file, data, samplerate, subtype='PCM_16')


            sampling_rate, audio = scipy.io.wavfile.read(file)
            if (len(audio.shape)==2):
                audio = audio.sum(axis=1) // 2
            number_of_samples = round(len(audio) * float(new_rate) / sampling_rate)
            audio = scipy.signal.resample(audio, number_of_samples)
            audio = audio.astype(dtype = np.int16)
            scipy.io.wavfile.write(file, new_rate, audio)

# нормализация wav-файлов по списку файлов source_files
def norm_audio(source_files):
        '''Normalize the audio files before training'''

        for file in source_files:
            audio, sr = librosa.load(file, sr=8000)
            div_fac = 1 / np.max(np.abs(audio)) / 3.0
            audio = audio * div_fac
            sf.write(file, audio, sr)
            print("normalization file = ", file)


# Параметры генерации датасета
path_source = './sources'
path_dataset = './dataset/'
dataset_csv='dataset.csv'

fs = 8000
length_track = 5 #seconds

print("\n Start create dataset ...")

source_files = find_files(path_source)
##downsampling(source_files)
norm_audio(source_files)

#Удалить все файлы в папке %path_dataset%
filelist = [ f for f in os.listdir(path_dataset) if f.endswith(".wav") ]
for f in filelist:
    os.remove(os.path.join(path_dataset, f))

#удалить файл %dataset_csv%
if os.path.isfile(dataset_csv):
    os.remove(dataset_csv)

number = 0

#index of csv
csv_data = [['file_name', 'class', 'length', 'file_name_source'],]

class_to_cut_5seconds = ['bigtown', 'splash', 'drilling', 'instrumental', 'multi-120voices', 'multitalking', 'multitalking-music',
    'engine-idling', 'street-music','multitalking-music-all-scenes-test']

class_to_cut_30seconds = ['voice33', 'voice34']

for i in range(len(source_files)):
    wave_data, sr = librosa.load(source_files[i], sr=8000)
    noise_class = os.path.split(source_files[i])[0]
    noise_class = os.path.split(noise_class)[1]
    source_name_file = os.path.split(source_files[i])[1]

    step_5sec = 5 * fs
    step_30sec = 30 * fs

    if (noise_class in class_to_cut_30seconds):

        for j in range(0, len(wave_data), step_30sec):
            wav_file = wave_data[j:j + step_30sec]

            len_wav = len(wav_file)//8000
            if (len_wav <= 2):
                continue

            file_name = "{0:=09d}.wav".format(number)
            wave_file_out = path_dataset + file_name
            print("create track " + str(number) + " for dataset from file = " + source_files[i] + "     write file = " + wave_file_out + "   len wav = " + str(len_wav))

            csv_data.append([file_name, noise_class, str(len_wav), source_name_file])

            sf.write(wave_file_out, wav_file, sr)
            number += 1

    else:
         for j in range(0, len(wave_data), step_5sec):
            wav_file = wave_data[j:j + step_5sec]

            len_wav = len(wav_file)//8000
            if (len_wav <= 2):
                continue

            file_name = "{0:=09d}.wav".format(number)
            wave_file_out = path_dataset + file_name
            print("create track " + str(number) + " for dataset from file = " + source_files[i] + "     write file = " + wave_file_out + "   len wav = " + str(len_wav))

            csv_data.append([file_name, noise_class, str(len_wav), source_name_file])

            sf.write(wave_file_out, wav_file, sr)
            number += 1


with open(dataset_csv, 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(csv_data)

dataset_files = find_files(path_dataset)
norm_audio(dataset_files)

print("\n Dataset created")

