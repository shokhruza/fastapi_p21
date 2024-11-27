import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import requests
from fastapi.templating import Jinja2Templates
from fastapi_storages import FileSystemStorage

load_dotenv()


@dataclass
class BaseConfig:
    def asdict(self):
        return asdict(self)


@dataclass
class DatabaseConfig(BaseConfig):
    """Database connection variables"""
    NAME: str = os.getenv('DB_NAME')
    USER: str = os.getenv('DB_USER')
    PASS: str = os.getenv('DB_PASS')
    HOST: str = os.getenv('DB_HOST')
    PORT: str = os.getenv('DB_PORT')

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"


@dataclass
class Configuration:
    """All in one configuration's class"""
    db = DatabaseConfig()
    SECRET_KEY: str = os.getenv('SECRET_KEY')


class CustomFileSystemStorage(FileSystemStorage):

    def __init__(self, path: str) -> None:
        date = datetime.today()
        super().__init__(os.path.join('media', date.strftime(path)))

def get_currency_in_sum() -> tuple[Optional[int], bool]:
    url = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for currency in data:
            if currency['Ccy'] == 'USD':
                return int(float(currency['Rate'])), True
    return None, False

conf = Configuration()
storage = CustomFileSystemStorage
templates = Jinja2Templates(directory='templates')