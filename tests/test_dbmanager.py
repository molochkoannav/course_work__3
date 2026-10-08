import unittest
from unittest.mock import MagicMock


from src.dbmanager import DBManager


class TestDBManager(unittest.TestCase):

    def setUp(self):
        # Создаем объект без вызова __init__
        self.db_manager = DBManager.__new__(DBManager)
        self.db_manager.conn = MagicMock()

    def test_get_countries_and_aeroplanes_count(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("USA", 150), ("Russia", 100), ("Germany", 50)]
        self.db_manager.conn.cursor.return_value = mock_cursor

        result = self.db_manager.get_countries_and_aeroplanes_count()

        mock_cursor.execute.assert_called_once()
        expected = [("USA", 150), ("Russia", 100), ("Germany", 50)]
        self.assertEqual(result, expected)

    def test_get_all_aeroplanes(self):
        mock_cursor = MagicMock()
        test_planes = [(1, "AAL123", 450, 10000, 1), (2, "UAL456", 500, 11000, 2), (3, "DAL789", 350, 9000, 3)]
        mock_cursor.fetchall.return_value = test_planes
        self.db_manager.conn.cursor.return_value = mock_cursor

        result = self.db_manager.get_all_aeroplanes()

        mock_cursor.execute.assert_called_once_with("SELECT * FROM aircraft_states")
        self.assertEqual(result, test_planes)

    def test_get_avg_speed(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (450.5,)
        self.db_manager.conn.cursor.return_value = mock_cursor

        result = self.db_manager.get_avg_speed()

        mock_cursor.execute.assert_called_once_with("SELECT AVG(velocity) FROM aircraft_states")
        self.assertEqual(result, 450.5)

    def test_get_aeroplanes_with_lower_speed(self):
        mock_cursor = MagicMock()
        test_planes = [(1, "AAL123", 300, 10000, 1), (2, "UAL456", 250, 11000, 2)]
        mock_cursor.fetchall.return_value = test_planes
        self.db_manager.conn.cursor.return_value = mock_cursor

        result = self.db_manager.get_aeroplanes_with_lower_speed()

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM aircraft_states WHERE velocity < (SELECT AVG(velocity) FROM aircraft_states)"
        )
        self.assertEqual(result, test_planes)

    def test_get_aeroplanes_with_keyword(self):
        mock_cursor = MagicMock()
        test_planes = [(1, "AAL123", 450, 10000, 1), (2, "AAL456", 500, 11000, 2)]
        mock_cursor.fetchall.return_value = test_planes
        self.db_manager.conn.cursor.return_value = mock_cursor

        keyword = "AAL"
        result = self.db_manager.get_aeroplanes_with_keyword(keyword)

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM aircraft_states WHERE aircraft_states.callsign LIKE %s", (f"%{keyword}%",)
        )
        self.assertEqual(result, test_planes)
