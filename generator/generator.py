import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from os import environ
from typing import TypedDict
from uuid import uuid4

import requests


class Generator:
    logger = logging.getLogger(__name__)
    
    class KeyInfo(TypedDict):
        key_ref: str
        key: str
        iv: str
        expire_date: datetime

    @classmethod
    def change_key(cls):
        new_key = secrets.token_bytes(16)
        new_iv = secrets.token_hex(16).upper()
        key_info = cls.generate_new_key_info(new_key, new_iv)
        saved_in_db = cls.send_key_to_kms(key_info)
        if not (saved_in_db):
            cls.add_key_info_to_queue(key_info)

        cls.write_key_info_ffmpeg(key_info["key_ref"], new_key, new_iv)

    @ classmethod
    def generate_new_key_info(cls, key, iv) -> KeyInfo:
        expire_time = int(environ.get("EXPIRE_TIME"))
        expire_date = (datetime.now() + timedelta(hours=expire_time)).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        key_info: cls.KeyInfo = {  # noqa
            "key_ref": str(uuid4()),
            "key": key.hex(),
            "init_vector": iv,
            "expire_date": expire_date,
        }
        cls.logger.info(f"Generated new key: {key_info['key_ref']}")
        return key_info

    @classmethod
    def send_key_to_kms(cls, key_info):
        url = environ.get("KMS_URL")
        auth_token = environ.get("KMS_TOKEN")
        try:
            respond = requests.post(
                url,
                headers={"Authorization": "Token " + auth_token},
                data=key_info,
            )

            if respond.status_code == 201:
                cls.logger.debug(f"Uploaded key: {key_info['key_ref']}")
                return True
            else:
                cls.logger.warning(
                    f"HTTP Request completed but with invalid response code. "
                    f"Key is not saved in database. "
                    f"Response Code: {respond.status_code}"
                )
                return False
        except Exception as e:  # noqa: E722
            cls.logger.warning(
                f"Error in Http Request. Key is not saved in database. Error: {e}"
            )
            return False

    @classmethod
    def write_key_info_ffmpeg(cls, key_ref, key, iv):
        key_uri = key_ref
        key_info_file = cls.get_ffmpeg_info_path() + "key_info"
        encryption_key_file = cls.get_ffmpeg_info_path() + "enc.key"
        with open(encryption_key_file, "wb") as key_file:
            cls.logger.debug(f"Writing key file: {key_ref}")
            key_file.write(key)
        write_text = key_uri + "\n" + encryption_key_file + "\n" + iv
        with open(key_info_file, "w") as key_info_file:
            cls.logger.debug(f"Writing key info file: {key_ref}")
            key_info_file.write(write_text)

    @staticmethod
    def get_ffmpeg_info_path():
        path = "/srv/keys/" + environ.get("CHANNEL_NAME") + "/"
        if not (os.path.exists(path)):
            os.mkdir(path)
        return path

    @classmethod
    def add_key_info_to_queue(cls, key_info):
        queue_path = cls.get_queue_path()
        file_exists = os.path.exists(queue_path)

        if file_exists:
            with open(queue_path, "r") as queue_file:
                cls.logger.debug("Reading existing queue")
                data = json.load(queue_file)
        else:
            data = {"queue": []}

        with open(queue_path, "w") as queue_file:
            cls.logger.debug(f"Adding Key to queue: {key_info['key_ref']}")
            data["queue"].append(key_info)
            cls.logger.debug("Writing Queue")
            json.dump(data, queue_file)

    @classmethod
    def upload_queue_to_kms(cls):
        queue_path = cls.get_queue_path()
        if os.path.isfile(queue_path):
            with open(queue_path, "r") as queue_file:
                data = json.load(queue_file)
            new_content = {"queue": []}
            for key_info in data["queue"]:
                cls.logger.info(f"Uploading key: {key_info['key_ref']}")
                uploaded = Generator.send_key_to_kms(key_info)
                if not uploaded:
                    new_content["queue"].append(key_info)

            with open(queue_path, "w") as queue_file:
                json.dump(new_content, queue_file)

    @staticmethod
    def get_queue_path() -> str:
        return "/srv/queues/" + environ.get("CHANNEL_NAME") + ".json"
