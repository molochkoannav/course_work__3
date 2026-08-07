import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch
from src.api import ApiAircrafts
from src.api import ApiBBox

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestApiBBox(unittest.TestCase):
    """Тесты для класса ApiBBox"""

    def test_init_default_countries(self):
        """Тест инициализации с стандартными странами"""
        api = ApiBBox()
        expected_countries = ["Ireland", "Greece", "Malaysia", "New_Zealand"]
        self.assertEqual(api.countries, expected_countries)
        self.assertEqual(api._ApiBBox__url, "https://nominatim.openstreetmap.org/search")
        self.assertEqual(api._ApiBBox__headers["User-Agent"], "test-app/1.0")

    def test_init_custom_countries(self):
        """Тест инициализации с пользовательским списком стран"""
        custom_countries = ["Russia", "USA", "China"]
        api = ApiBBox(custom_countries)
        self.assertEqual(api.countries, custom_countries)

    @patch("src.api.requests.get")
    def test_get_response_success(self, mock_get):
        """Тест успешного получения ответа от API"""
        # Подготовка мок-данных
        mock_response = Mock()
        mock_response.json.return_value = [
            {"boundingbox": ["53.0", "54.0", "-8.0", "-7.0"], "display_name": "Ireland"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызов метода
        api = ApiBBox(["Ireland"])
        result = api.get_response()

        # Проверки
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0]["display_name"], "Ireland")
        mock_get.assert_called_once()

    @patch("src.api.requests.get")
    def test_get_data_success(self, mock_get):
        """Тест успешного получения и обработки данных"""
        # Подготовка мок-данных
        mock_response = Mock()
        mock_response.json.return_value = [
            {"boundingbox": ["53.0", "54.0", "-8.0", "-7.0"], "display_name": "Ireland"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызов метода
        api = ApiBBox(["Ireland"])
        result = api.get_data()

        # Проверки
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ["53.0", "54.0", "-8.0", "-7.0"])

    def test_empty_countries_list(self):
        """Тест с пустым списком стран"""
        api = ApiBBox([])
        result = api.get_response()
        self.assertEqual(result, [])

    @patch("src.api.requests.get")
    def test_get_response_multiple_countries(self, mock_get):
        """Тест получения данных для нескольких стран"""
        # Подготовка мок-данных
        mock_response1 = Mock()
        mock_response1.json.return_value = [{"boundingbox": ["53.0", "54.0", "-8.0", "-7.0"]}]
        mock_response1.raise_for_status.return_value = None

        mock_response2 = Mock()
        mock_response2.json.return_value = [{"boundingbox": ["37.0", "38.0", "23.0", "24.0"]}]
        mock_response2.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response1, mock_response2]

        # Вызов метода
        api = ApiBBox(["Ireland", "Greece"])
        result = api.get_response()

        # Проверки
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_get.call_count, 2)


class TestApiAircrafts(unittest.TestCase):
    """Тесты для класса ApiAircrafts"""

    def test_init(self):
        """Тест инициализации"""
        bbox = [["53.0", "54.0", "-8.0", "-7.0"]]
        api = ApiAircrafts(bbox)
        self.assertEqual(api._ApiAircrafts__url, "https://opensky-network.org/api/states/all")
        self.assertEqual(api._ApiAircrafts__bbox_cords, bbox)

    @patch("src.api.requests.get")
    def test_get_response_success(self, mock_get):
        """Тест успешного получения данных о самолетах"""
        # Подготовка мок-данных
        mock_aircraft_data = {
            "time": 1234567890,
            "states": [
                [
                    "abc123",
                    "Flight1",
                    "Ireland",
                    1234567890,
                    53.5,
                    -7.5,
                    10000,
                    False,
                    300,
                    280,
                    10,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ]
            ],
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_aircraft_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызов метода
        bbox = [["53.0", "54.0", "-8.0", "-7.0"]]
        api = ApiAircrafts(bbox)
        result = api.get_response()

        # Проверки
        self.assertEqual(len(result), 1)
        self.assertIn("states", result[0])
        self.assertEqual(len(result[0]["states"]), 1)
        mock_get.assert_called_once()

    @patch("src.api.requests.get")
    def test_get_response_no_states(self, mock_get):
        """Тест получения ответа без данных о самолетах"""
        # Подготовка мок-данных
        mock_response = Mock()
        mock_response.json.return_value = {"time": 1234567890, "states": None}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызов метода
        bbox = [["53.0", "54.0", "-8.0", "-7.0"]]
        api = ApiAircrafts(bbox)
        result = api.get_response()

        # Проверки
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["states"])

    @patch("src.api.requests.get")
    def test_get_data_success(self, mock_get):
        """Тест успешного получения и обработки данных о самолетах"""
        # Подготовка мок-данных
        mock_aircraft_data = {
            "time": 1234567890,
            "states": [
                [
                    "abc123",
                    "Flight1",
                    "Ireland",
                    1234567890,
                    53.5,
                    -7.5,
                    10000,
                    False,
                    300,
                    280,
                    10,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ]
            ],
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_aircraft_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызов метода
        bbox = [["53.0", "54.0", "-8.0", "-7.0"]]
        api = ApiAircrafts(bbox)
        result = api.get_data()

        # Проверки
        self.assertEqual(len(result), 1)
        self.assertIn("states", result[0])
        self.assertEqual(len(result[0]["states"]), 1)

    @patch("src.api.requests.get")
    def test_multiple_bboxes(self, mock_get):
        """Тест с несколькими bbox"""
        # Подготовка мок-данных
        mock_response1 = Mock()
        mock_response1.json.return_value = {"time": 1234567890, "states": [["flight1", "Flight1"]]}
        mock_response1.raise_for_status.return_value = None

        mock_response2 = Mock()
        mock_response2.json.return_value = {"time": 1234567890, "states": [["flight2", "Flight2"]]}
        mock_response2.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response1, mock_response2]

        # Вызов метода
        bbox = [["53.0", "54.0", "-8.0", "-7.0"], ["37.0", "38.0", "23.0", "24.0"]]
        api = ApiAircrafts(bbox)
        result = api.get_response()

        # Проверки
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_get.call_count, 2)
