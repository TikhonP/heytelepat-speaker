#!/usr/bin/env python

"""
`issue_manager.py`
Commit speaker log util
OOO Telepat, All Rights Reserved
"""

__version__ = '0.0.4'
__author__ = 'Tikhon Petrishchev'
__credits__ = 'TelePat LLC'

import asyncio
import configparser
import json
import logging
import os
import subprocess
from pathlib import Path
import time

import requests
import websockets

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILENAME = os.path.join(BASE_DIR, 'src/settings.ini')
CONFIG_FILENAME = os.path.join(Path.home(), '.speaker/config.json')


def get_settings():
    """Load ini config and generates dictionary"""

    global SETTINGS_FILENAME

    with open(SETTINGS_FILENAME):
        pass

    config = configparser.ConfigParser()
    config.read(SETTINGS_FILENAME)
    logging.info("Loaded settings from `{}`.".format(SETTINGS_FILENAME))
    return config


def get_token():
    """Load token if exists

    :return: string token if exists
    :rtype: str | None
    """

    global CONFIG_FILENAME
    try:
        with open(CONFIG_FILENAME) as f:
            config = json.load(f)
            return config.get('token')
    except FileNotFoundError:
        logging.warning("Config not found in `{}`.".format(CONFIG_FILENAME))
        return


def check_connection_ping(host='google.com'):
    """
    Ping to host and if success return True else False

    :param string host: Host to ping, default 'google.com'
    :return: Connection exist or not
    :rtype: boolean
    """

    subprocess_return = subprocess.run(
        ['timeout', '1.5', 'ping', '-c', '1', host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return subprocess_return.returncode == 0


async def on_message(host: str, issue_id: int, token: str):
    global BASE_DIR

    file_path = os.path.join(BASE_DIR, 'issue_manager', f'issue_{issue_id}.log')
    logging.info("Got issue ({}), dumping log -> `{}`".format(issue_id, file_path))

    subprocess.run(
        [os.path.join(BASE_DIR, 'issue_manager', 'dump_log.sh'), file_path],
        stdout=subprocess.PIPE
    )

    url = f'https://{host}/staff/issue/log/{issue_id}/{token}/'
    with open(file_path, 'rb') as f:
        files = {'upload_file': f}
        answer = requests.post(url, files=files)

    answer.raise_for_status()

    os.remove(file_path)
    logging.info("Successfully sent log and removed file.")


async def websocket_connect(host: str, token: str):
    url = f'wss://{host}/ws/staff/issue/'
    init_message = {'token': token}

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps(init_message))
            logging.info("Connected to websocket, listening")
            while True:
                if message := json.loads(await ws.recv()):
                    await on_message(host, message.get('id'), token)
    except websockets.exceptions.ConnectionClosedError:
        logging.warning("Broke connection with socket, retrying to connect...")
        return


async def main():
    while not check_connection_ping():
        logging.error("Network unavilible waiting...")
        time.sleep(5)

    settings = get_settings()

    token = get_token()
    while token is None:
        logging.error("Token unavailible waiting...")
        time.sleep(5)
        token = get_token()

    while True:
        await websocket_connect(settings['SERVER']['HOST'], token)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    logging.info("Issue manager speaker firmware util [{}]. `OOO Telepat` All Rights Reserved.".format(__version__))
    asyncio.run(main())
