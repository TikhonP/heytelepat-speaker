from network import network
import ggwave
import pyaudio
import json
import time
import logging


def get_ggwave_input():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paFloat32, channels=1,
                    rate=48000, input=True, frames_per_buffer=1024)

    instance = ggwave.init()

    while True:
        data = stream.read(1024, exception_on_overflow=False)
        res = ggwave.decode(instance, data)
        if res is not None:
            try:
                data_str = res.decode('utf-8')
                return data_str
            except ValueError:
                pass

    ggwave.free(instance)

    stream.stop_stream()
    stream.close()

    p.terminate()


def wirless_network_init(objectStorage, first=False):
    if first:
        objectStorage.speakSpeach.play("Привет! Это колонка Telepat Medsenger."
                         "Для начала работы необходимо подключение к сети."
                         "Для это сгенерируйте аудиокод с паролем от Wi-Fi.",
                         cashed=True)
    else:
        objectStorage.speakSpeach.play("К сожалению подключиться не удалось, "
                         "Попробуйте сгенерировать код еще раз.", cashed=True)

    objectStorage.pixels.think()
    data = get_ggwave_input()
    data = json.loads(data)

    n = network.Network(data['ssid'])
    if not n.check_available():
        logging.info("Network is unavailable")
        objectStorage.speakSpeach.play(
            "Пока что сеть недоступна, продолжается попытка подключения",
            cashed=True)

    objectStorage.pixels.think()
    n.create(data['psk'])
    if not n.connect():
        logging.error("Connection error")


def ConnectionGate(objectStorage):
    objectStorage.pixels.wakeup()
    first = True
    while not network.check_connection_hardware() or \
            not network.check_really_connection():
        logging.warning("No connection detected")
        wirless_network_init(objectStorage, first)
        first = False
        time.sleep(5)

    logging.info("Connection exists")
    objectStorage.speakSpeech.play(
        "Подключение к беспроводной сети произошло успешно", cashed=True)


def cash_phrases(speakSpeech):
    data = [
        "Привет! Это колонка Telepat Medsenger."
        "Для начала работы необходимо подключение к сети."
        "Для это сгенерируйте аудиокод с паролем от Wi-Fi.",
        "К сожалению подключиться не удалось, "
        "Попробуйте сгенерировать код еще раз.",
        "Пока что сеть недоступна, продолжается попытка подключения",
        "Подключение к беспроводной сети произошло успешно"
    ]

    for phrase in data:
        speakSpeech.cash_only(phrase)