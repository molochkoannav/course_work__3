from abc import ABC,abstractmethod
import requests
import time
import logging
import os
from pathlib import Path
from datetime import datetime
from src.logger import Logger


project_root = Path(__file__).parent.parent
logs_dir = project_root / 'logs'
logs_dir.mkdir(exist_ok=True)
log_filename = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

Logger.configure(
    console_output=False,
    level=logging.DEBUG,
    log_file=str(log_filename),
    format_str='%(asctime)s - %(funcName)s - %(pathname)s - %(levelname)s - %(message)s'
)


log = Logger(__name__)


class BaseApi(ABC):
    """Базовык класс для получения данных по api"""
    @abstractmethod
    def get_response(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

class ApiBBox(BaseApi):
    """Класс получает данные о координатах стран"""
    def __init__(self, countries=None):
        # Если список не передан, используем стандартный
        if countries is None:
            self.countries = ["Ireland", "Greece", "Malaysia", "New_Zealand"]
        else:
            self.countries = countries
        self.__url = "https://nominatim.openstreetmap.org/search"
        self.__headers = {
            'User-Agent': 'test-app/1.0',
        }
        self.__params = {
            'format': 'json',
            'limit': 1,
        }

    def get_response(self):
        """Получаем данные о координатах стран"""
        countries = self.countries
        data_cords = []
        for country in countries:
            self.__params['country'] = country
            response = requests.get(self.__url,params=self.__params,  headers=self.__headers)
            log.info("Данные получены")
            response.raise_for_status()
            data_cords.append(response.json())
            time.sleep(1)

        return data_cords

    def get_data(self):
        """Из данных достаем только координаты стран"""
        all_bboxes = []
        responses = self.get_response()
        for response in responses:
            all_bboxes.append(response[0]['boundingbox'])
            log.info(f"Получено bbox для {len(all_bboxes)} стран")
        return all_bboxes

class ApiAircrafts(BaseApi):
    """Класс получает данные о самолетах в воздушных пространствах выбранных стран"""
    def __init__(self, all_bboxes):
        self.__url = "https://opensky-network.org/api/states/all"
        self.__bbox_cords = all_bboxes

    def get_response(self):
        """Получаем данные о самолетах в воздушном пространстве стран"""
        aicraft_data = []
        for bbox in self.__bbox_cords:
            params = {
                'lamin': bbox[0],
                'lamax': bbox[1],
                'lomin': bbox[2],
                'lomax': bbox[3],
            }

            response = requests.get(self.__url, params=params)
            log.info("Данные о самолетах получены")
            response.raise_for_status()
            aicraft_data.append(response.json())

        return aicraft_data

    def get_data(self):
        """Достаем данные о самолетах"""
        aircrafts = self.get_response()
        for data in aircrafts:
            if 'states' in data and data['states']:
                data['states'] = data['states']
        log.info(f"Получено данных о {len(aircrafts)} самолетах")
        return aircrafts
