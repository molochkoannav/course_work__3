from abc import ABC,abstractmethod
import requests
import time
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
            response.raise_for_status()
            aicraft_data.append(response.json())
        return aicraft_data

    def get_data(self):
        """Достаем данные о самолетах"""
        aircrafts = self.get_response()
        for data in aircrafts:
            if 'states' in data and data['states']:
                data['states'] = data['states'][:20]
        return aircrafts

if __name__ == '__main__':
    bbox_api_default = ApiBBox()  # Используем Ireland, Greece, Malaysia, New_Zealand
    bboxes = bbox_api_default.get_data()
    print(f"Получено bbox для {len(bboxes)} стран")
    if bboxes:
        airplanes = ApiAircrafts(bboxes)
        aircraft_data = airplanes.get_data()
        print(airplanes.get_data())

        # Общее количество самолетов над всеми странами
        total_aircraft = 0
        for i, data in enumerate(aircraft_data):
            states = data.get('states')
            if states:
                count = len(states)
                total_aircraft += count
                print(f"Страна {i + 1}: {count} самолетов")

        print(f"Всего самолетов над всеми странами: {total_aircraft}")