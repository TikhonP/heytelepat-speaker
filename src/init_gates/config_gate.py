import asyncio
import configparser
import functools
import json
import logging
import os
from pathlib import Path

import requests
from speechkit import Session
from speechkit.auth import generate_jwt

from core import pixels, sound_processor
from core.speech import (
    PlaySpeech,
    ListenRecognizeSpeech,
    raspberry_simple_audio_play_audio_function,
    default_play_audio_function
)


class ObjectStorage:
    """Stores all objects for speaker functioning"""

    def __init__(self, config, **kwargs):
        """
        :param dict config: Data from speaker_config.json file
        :param string config_filename: File path to config

        :param function input_function: Function that captures voice action, default `lambda: input("Press enter.")`
        :param string config_filename: Path to config file, default `~/.speaker/config.json`
        :param boolean development: If development mode, default `False`
        :param boolean debug_mode: Debug mode status, default `None`
        :param string cash_filename: File path of cash file, default get from config
        :param string version: Version of script like `major.minor.fix`, default `null`

        :return: __init__ should return None
        :rtype: None
        """

        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.config = config

        self.inputFunction = kwargs.get('input_function')
        self.config_filename = kwargs.get('config_filename', os.path.join(Path.home(), '.speaker/config.json'))
        self.development = kwargs.get('development', False)
        self.debug_mode = kwargs.get('debug_mode')
        self.cash_filename = kwargs.get('cash_filename', os.path.join(Path.home(), '.speaker/speech.cash'))
        self.version = kwargs.get('version', 'null')

        self.event_loop = asyncio.get_event_loop()
        self.pixels = pixels.Pixels(self.development)
        try:
            self.session = Session.from_jwt(self.speechkit_jwt_token)
        except requests.exceptions.ConnectionError:
            self.session = None

        self.play_speech = PlaySpeech(self.session, self.cash_filename, self.pixels)

        if self.session:
            self.listen_recognize_speech = ListenRecognizeSpeech(self.session, self.pixels)

    def init_speechkit(self):
        self.session = Session.from_jwt(self.speechkit_jwt_token)
        play_audio_function = default_play_audio_function if self.development else \
            raspberry_simple_audio_play_audio_function
        self.play_speech = PlaySpeech(self.session, self.cash_filename, self.pixels, play_audio_function)
        self.listen_recognize_speech = ListenRecognizeSpeech(self.session, self.pixels)

    @staticmethod
    def _get_location_data():
        answer = requests.get('http://ipinfo.io/json')
        if answer.ok:
            return answer.json()
        else:
            return {}

    @property
    def speechkit_jwt_token(self):
        """
        JWT token for speechkit

        :return: Jwt token or None if not found
        :rtype: str | None
        """
        with open(self.config.get('speechkit_private_key_filename'), 'rb') as f:
            private_key = f.read()
        return generate_jwt(
            self.config.get('speechkit_service_account_id'),
            self.config.get('speechkit_key_id'),
            private_key
        )

    @functools.cached_property
    def host(self):
        """
        Host of heytelepat-server

        :return: Host in format domain only like 'google.com'
        :rtype: string | None
        """
        return self.config.get('host')

    @functools.cached_property
    def host_http(self, prefix='http://', postfix='/speaker/api/v1/'):
        """
        URL for HTTP requests

        :param string prefix: HTTP prefix, default `http://`
        :param string postfix: Base API url, default `/speaker/api/v1/`
        :return: Full URL for http request, like `http://domain.com/speaker/api/v1/`,
        if `ObjectStorage.host` is not None
        :rtype: string | None
        """
        return prefix + self.host + postfix if self.host else None

    @functools.cached_property
    def host_ws(self, prefix='ws://', postfix='/ws/speakerapi/'):
        """
        URL for websockets requests

        :param string prefix: HTTP prefix, default `ws://`
        :param string postfix: Base API url, default `/ws/speakerapi/`
        :return: Full URL for websocket request, like `ws://domain.com/`
        :rtype: string
        """
        return prefix + self.host + postfix if self.host else None

    @functools.cached_property
    def token(self):
        """
        Token of heytelepat-speaker server, to reset cash call `del ObjectStorage.token`

        :rtype: string | None
        """
        return self.config.get('token')

    @functools.cached_property
    def weather_token(self):
        return self.config.get('weather_token')

    @functools.cached_property
    def city(self):
        return self._get_location_data().get('city')

    @functools.cached_property
    def region(self):
        return self._get_location_data().get('region')

    @functools.cached_property
    def country(self):
        return self._get_location_data().get('country')

    @functools.cached_property
    def timezone(self):
        return self._get_location_data().get('timezone')


def get_settings():
    """
    Load ini config and generates dictionary

    :rtype: dict
    """
    logging.info("First loading from `settings.ini`")
    settings_filename = os.path.join(Path(__file__).resolve().parent.parent, 'settings.ini')

    if not Path(settings_filename).resolve().is_file():
        raise FileNotFoundError("No such file or directory: '{}'".format(settings_filename))

    config = configparser.ConfigParser()
    config.read(settings_filename)

    return {
        'speechkit_service_account_id': config['SPEECHKIT']['SERVICE_ACCOUNT_ID'],
        'speechkit_key_id': config['SPEECHKIT']['KEY_ID'],
        'speechkit_private_key_filename': config['SPEECHKIT']['PRIVATE_KEY_FILENAME'],
        'host': config['SERVER']['HOST'],
        'version': config['GLOBAL']['VERSION'],
        'weather_token': config['WEATHER']['TOKEN']
    }


def save_config(config: dict, file_path: str):
    logging.info("Saving config to `{}`".format(file_path))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(config, f)


def load_config(file_path):
    """
    Load config file if exists

    :param string file_path: Path to config file
    :return: Optional python dict with config
    :rtype: dict | None
    """
    try:
        with open(file_path) as f:
            config = json.load(f)
        logging.info("Loaded config with filename `{}`".format(file_path))
        return config
    except FileNotFoundError:
        return


def config_gate(
        input_function,
        debug_mode=False,
        reset=False,
        clean_cash=False,
        development=False,
        version=None
):
    """Default config file stores in ~/.speaker/config.json"""

    config_file_path = os.path.join(Path.home(), '.speaker/config.json')

    if not (config := load_config(config_file_path)):
        config = get_settings()
        config['token'] = None
    else:
        config.update(get_settings())

    if reset:
        logging.info("Resetting token")
        config['token'] = None

    save_config(config, config_file_path)

    if input_function == 'rpi_button':
        logging.info("Setup input function as Button")
        input_function = sound_processor.raspberry_input_function
    elif input_function == 'wake_up_word':
        logging.info("Setup wake_up_word input function")
        input_function = sound_processor.wakeup_word_input_function
    elif input_function == 'simple':
        logging.info("Setup input simple input function")
        input_function = sound_processor.async_simple_input_function
    else:
        raise ValueError(
            "Invalid input fiction '{}'. ".format(input_function) +
            "Available options: ['simple', 'rpi_button', 'wake_up_word']")

    object_storage = ObjectStorage(
        config,
        input_function=input_function,
        config_filename=config_file_path,
        development=development,
        debug_mode=debug_mode,
        version=version
    )

    if object_storage.version != config.get('version'):
        raise ValueError("Main file version ({}) and config version ({}) didn't match!".format(
            object_storage.version, config.get('version')))

    if clean_cash:
        logging.info("Cleanup cash")
        object_storage.play_speech.reset_cash()

    return object_storage
