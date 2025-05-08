import csv
import os
import time
import requests
from gtts import gTTS # Для озвучки текста в речь
from phonemizer import phonemize # Для получения транскрипции слов
from dotenv import load_dotenv # Для загрузки API-ключей из .env
from PIL import Image # (Пока не используется, можно удалить или использовать)

# Указываем путь к eSpeak (если установлен espeak-ng)
os.environ["PATH"] += os.pathsep + r"C:\Program Files\eSpeak NG"

# Настройки
WORDS_FILE = "words.txt"
CSV_FILE = "anki_deck.csv"
AUDIO_FOLDER = "audio"
IMAGE_FOLDER = "images"

load_dotenv()  # Загружает переменные из .env
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Функция для генерации транскрипции
def get_transcription(word):
    return phonemize(word, language="en-us", backend="espeak", strip=True)

# Функция для генерации озвучки
def generate_audio(word, filename):
    tts = gTTS(word, lang="en")
    tts.save(filename)

# Функция для перевода слова
def translate_word(word):
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ru&dt=t&q={word}"
    try:
        response = requests.get(url).json()
        return response[0][0][0]
    except:
        return ""

# Функция для поиска примеров предложений
def get_example_sentence(word):
    url = f"https://tatoeba.org/en/api_v0/search?query={word}&from=eng&to=rus&orphans=no&unapproved=no"
    try:
        response = requests.get(url).json()
        for item in response['results']:
            eng = item['text']
            rus = item['translations'][0]['text']
            return eng, rus
    except:
        return "", ""

# Функция для поиска картинок
def get_image(word, filename):
    url = f"https://api.pexels.com/v1/search?query={word}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        if response['photos']:
            image_url = response['photos'][0]['src']['medium']
            img_data = requests.get(image_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
    except:
        pass # Если что-то пошло не так — просто пропускаем

# Создаем папки
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Читаем слова
words = [line.strip() for line in open(WORDS_FILE, encoding="utf-8")]
data = [] # Сюда будут собираться строки для CSV-файла

for word in words:
    print(f"Обрабатываем: {word}")
    transcription = get_transcription(word)
    translation = translate_word(word)
    eng_sentence, rus_sentence = get_example_sentence(word)
    audio_file = f"{AUDIO_FOLDER}/{word}.mp3"
    image_file = f"{IMAGE_FOLDER}/{word}.jpg"

    generate_audio(word, audio_file)
    get_image(word, image_file)

    data.append([word, transcription, translation, eng_sentence, rus_sentence, audio_file, image_file])
    time.sleep(1) # Пауза между запросами, чтобы не забанили API

# Записываем в CSV
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Word", "Transcription", "Translation", "Example EN", "Example RU", "Audio", "Image"])
    writer.writerows(data)

print(f"Готово! Файл {CSV_FILE} создан.")
