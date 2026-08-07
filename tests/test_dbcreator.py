from unittest.mock import MagicMock
from unittest.mock import patch

import psycopg2
import pytest

from src.dbcreator import create_database
from src.dbcreator import save_data_to_db


class TestCreateDatabase:
    """Тесты для функции create_database"""

    @pytest.fixture
    def mock_config(self):
        """Фикстура для мока конфигурации"""
        with patch("src.dbcreator.config") as mock:
            mock.return_value = {"host": "localhost", "user": "test"}
            yield mock

    @pytest.fixture
    def mock_connect(self):
        """Фикстура для мока подключения к БД"""
        with patch("src.dbcreator.psycopg2.connect") as mock:
            yield mock

    def test_create_database_success(self, mock_config, mock_connect):
        """Успешное создание БД"""
        # Мок для первого соединения (проверка существования БД)
        mock_cursor1 = MagicMock()
        mock_cursor1.fetchone.return_value = None  # БД не существует
        mock_conn1 = MagicMock()
        mock_conn1.cursor.return_value = mock_cursor1

        # Мок для второго соединения (создание таблиц)
        mock_cursor2 = MagicMock()
        mock_conn2 = MagicMock()
        # Настройка для работы с контекстным менеджером
        mock_conn2.cursor.return_value.__enter__.return_value = mock_cursor2
        mock_conn2.cursor.return_value.__exit__.return_value = False

        mock_connect.side_effect = [mock_conn1, mock_conn2]

        # Вызов тестируемой функции
        create_database("test_db")

        # Проверяем, что был вызов для проверки существования БД
        mock_cursor1.execute.assert_any_call("SELECT 1 FROM pg_database WHERE datname = %s", ("test_db",))

        # Проверяем, что был вызов CREATE DATABASE
        create_calls = [call for call in mock_cursor1.execute.call_args_list if "CREATE DATABASE" in str(call)]
        assert len(create_calls) == 1, "CREATE DATABASE должен быть вызван"

        # Проверяем создание таблиц
        assert mock_cursor2.execute.call_count >= 2, "Должно быть минимум 2 вызова для создания таблиц"
        mock_conn2.commit.assert_called_once()

    def test_create_database_already_exists(self, mock_config, mock_connect):
        """БД уже существует - должна быть удалена и создана заново"""
        # Мок для первого соединения (проверка существования БД)
        mock_cursor1 = MagicMock()
        mock_cursor1.fetchone.return_value = [1]  # БД существует
        mock_conn1 = MagicMock()
        mock_conn1.cursor.return_value = mock_cursor1

        # Мок для второго соединения (создание таблиц)
        mock_cursor2 = MagicMock()
        mock_conn2 = MagicMock()
        # Настройка для работы с контекстным менеджером
        mock_conn2.cursor.return_value.__enter__.return_value = mock_cursor2
        mock_conn2.cursor.return_value.__exit__.return_value = False

        mock_connect.side_effect = [mock_conn1, mock_conn2]

        # Вызов тестируемой функции
        create_database("test_db")

        # Проверяем, что была проверка существования БД
        mock_cursor1.execute.assert_any_call("SELECT 1 FROM pg_database WHERE datname = %s", ("test_db",))

        # Проверяем, что был вызов для завершения подключений
        terminate_calls = [call for call in mock_cursor1.execute.call_args_list if "pg_terminate_backend" in str(call)]
        assert len(terminate_calls) == 1, "Должен быть вызов pg_terminate_backend"

        # Проверяем, что был вызов DROP DATABASE
        drop_calls = [call for call in mock_cursor1.execute.call_args_list if "DROP DATABASE" in str(call)]
        assert len(drop_calls) == 1, "DROP DATABASE должен быть вызван"

        # Проверяем, что был вызов CREATE DATABASE
        create_calls = [call for call in mock_cursor1.execute.call_args_list if "CREATE DATABASE" in str(call)]
        assert len(create_calls) == 1, "CREATE DATABASE должен быть вызван"

        # Проверяем создание таблиц
        assert mock_cursor2.execute.call_count >= 2, "Должно быть минимум 2 вызова для создания таблиц"
        mock_conn2.commit.assert_called_once()


class TestSaveDataToDb:
    """Тесты для функции save_data_to_db"""

    @pytest.fixture
    def sample_countries(self):
        """Фикстура с данными стран"""
        return {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"], "UK": ["50.0", "51.0", "-1.0", "0.0"]}

    @pytest.fixture
    def sample_aircraft(self):
        """Фикстура с данными самолетов"""
        return {
            "Ireland": [
                [
                    "abc123",
                    "FL123",
                    "Ireland",
                    123,
                    123,
                    53.5,
                    -7.5,
                    10000.0,
                    False,
                    300.0,
                    280.0,
                    10.0,
                    None,
                    10000.0,
                    "1234",
                    False,
                    1,
                    1,
                ]
            ],
            "UK": [
                [
                    "def456",
                    "FL456",
                    "UK",
                    456,
                    456,
                    50.5,
                    -0.5,
                    15000.0,
                    True,
                    450.0,
                    290.0,
                    5.0,
                    None,
                    15000.0,
                    "5678",
                    True,
                    2,
                    2,
                ]
            ],
        }

    @pytest.fixture
    def sample_countries_single(self):
        """Фикстура с одной страной"""
        return {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"]}

    @pytest.fixture
    def mock_config(self):
        """Фикстура для мока конфигурации"""
        with patch("src.dbcreator.config") as mock:
            mock.return_value = {"host": "localhost", "user": "test"}
            yield mock

    @pytest.fixture
    def mock_connect(self):
        """Фикстура для мока подключения к БД"""
        with patch("src.dbcreator.psycopg2.connect") as mock:
            yield mock

    def create_mock_cursor_with_fetchone(self, fetchone_values):
        """
        Создает мок-курсор с последовательностью значений для fetchone
        """
        cursor = MagicMock()

        # Создаем копию списка для работы
        values = list(fetchone_values)

        def fetchone_side_effect():
            if values:
                return values.pop(0)
            return None

        cursor.fetchone.side_effect = fetchone_side_effect

        # Настройка mogrify для execute_batch
        def mogrify_side_effect(sql, args):
            return b"INSERT INTO aircraft_states ..."

        cursor.mogrify = MagicMock(side_effect=mogrify_side_effect)

        return cursor

    def test_save_data_success(self, mock_config, mock_connect, sample_countries, sample_aircraft):
        """Успешное сохранение данных"""
        # Для двух стран: сначала None (нет в БД), потом ID для каждой
        mock_cursor = self.create_mock_cursor_with_fetchone([None, [1], None, [2]])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Вызов тестируемой функции
        result = save_data_to_db(sample_countries, sample_aircraft, "test_db")

        # Функция возвращает int - количество сохраненных записей
        assert isinstance(result, int), "Функция должна возвращать целое число"
        assert result == 2, f"Ожидалось 2 сохраненные записи, получено {result}"

        mock_conn.commit.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_save_data_update_existing(self, mock_config, mock_connect, sample_countries, sample_aircraft):
        """Обновление существующей страны"""
        # Страны уже существуют: возвращаем ID сразу
        mock_cursor = self.create_mock_cursor_with_fetchone([[1], [2]])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = save_data_to_db(sample_countries, sample_aircraft, "test_db")

        assert isinstance(result, int)
        assert result == 2, f"Ожидалось 2, получено {result}"
        mock_conn.commit.assert_called()

    def test_save_data_missing_coordinates(self, mock_config, mock_connect):
        """Пропуск страны без координат"""
        countries = {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"], "Unknown": []}
        aircraft = {
            "Ireland": [
                [
                    "abc123",
                    "FL123",
                    "Ireland",
                    123,
                    123,
                    53.5,
                    -7.5,
                    10000.0,
                    False,
                    300.0,
                    280.0,
                    10.0,
                    None,
                    10000.0,
                    "1234",
                    False,
                    1,
                    1,
                ]
            ],
            "Unknown": [
                ["def456", "FL456", "Unknown", 123, 123, 0, 0, 0, False, 0, 0, 0, None, 0, "0000", False, 1, 1]
            ],
        }

        # Только Ireland будет обработана (1 страна -> 2 значения)
        mock_cursor = self.create_mock_cursor_with_fetchone([None, [1]])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = save_data_to_db(countries, aircraft, "test_db")

        assert isinstance(result, int)
        assert result == 1, "Только Ireland должна быть сохранена"
        mock_conn.commit.assert_called()

    def test_save_data_country_not_found(self, mock_config, mock_connect, sample_countries):
        """Страна из aircraft отсутствует в countries_data"""
        aircraft = {
            "Ireland": [
                [
                    "abc123",
                    "FL123",
                    "Ireland",
                    123,
                    123,
                    53.5,
                    -7.5,
                    10000.0,
                    False,
                    300.0,
                    280.0,
                    10.0,
                    None,
                    10000.0,
                    "1234",
                    False,
                    1,
                    1,
                ]
            ],
            "Unknown": [
                ["def456", "FL456", "Unknown", 123, 123, 0, 0, 0, False, 0, 0, 0, None, 0, "0000", False, 1, 1]
            ],
        }

        # sample_countries содержит 2 страны -> нужно 4 значения
        mock_cursor = self.create_mock_cursor_with_fetchone([None, [1], None, [2]])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = save_data_to_db(sample_countries, aircraft, "test_db")

        assert isinstance(result, int)
        assert result == 1, "Только Ireland должна быть сохранена"
        mock_conn.commit.assert_called()

    def test_save_data_with_none_states(self, mock_config, mock_connect, sample_countries_single):
        """Обработка None в данных о самолетах"""
        aircraft = {
            "Ireland": [
                None,  # None вместо списка
                [
                    "abc123",
                    "FL123",
                    "Ireland",
                    123,
                    123,
                    53.5,
                    -7.5,
                    10000.0,
                    False,
                    300.0,
                    280.0,
                    10.0,
                    None,
                    10000.0,
                    "1234",
                    False,
                    1,
                    1,
                ],
            ]
        }

        # Одна страна -> 2 значения
        mock_cursor = self.create_mock_cursor_with_fetchone([None, [1]])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = save_data_to_db(sample_countries_single, aircraft, "test_db")

        assert isinstance(result, int)
        assert result == 1, "Только один валидный state должен быть сохранен"
        mock_conn.commit.assert_called()

    def test_save_data_empty_aircraft(self, mock_config, mock_connect, sample_countries_single):
        """Пустые данные о самолетах"""
        aircraft = {"Ireland": []}

        # Одна страна -> 2 значения
        mock_cursor = self.create_mock_cursor_with_fetchone([None, [1]])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = save_data_to_db(sample_countries_single, aircraft, "test_db")

        assert isinstance(result, int)
        assert result == 0, "Нет состояний для сохранения"
        mock_conn.commit.assert_called()

    def test_save_data_database_error(self, mock_config, mock_connect):
        """Ошибка базы данных"""
        mock_cursor = MagicMock()
        # Первый вызов fetchone вызывает ошибку
        mock_cursor.fetchone.side_effect = psycopg2.Error("Database error")

        def mogrify_side_effect(sql, args):
            return b"INSERT INTO aircraft_states ..."

        mock_cursor.mogrify = MagicMock(side_effect=mogrify_side_effect)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Вызов функции - должна вернуть 0 при ошибке
        result = save_data_to_db(
            {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"]},
            {
                "Ireland": [
                    [
                        "abc123",
                        "FL123",
                        "Ireland",
                        123,
                        123,
                        53.5,
                        -7.5,
                        10000.0,
                        False,
                        300.0,
                        280.0,
                        10.0,
                        None,
                        10000.0,
                        "1234",
                        False,
                        1,
                        1,
                    ]
                ]
            },
            "test_db",
        )

        assert result == 0, "При ошибке должно возвращаться 0"
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestSaveDataToDbParametrized:
    """Параметризованные тесты для функции save_data_to_db"""

    @pytest.fixture
    def mock_db(self):
        """Фикстура для мока БД"""
        with patch("src.dbcreator.config") as mock_config:
            mock_config.return_value = {"host": "localhost", "user": "test"}

            with patch("src.dbcreator.psycopg2.connect") as mock_connect:
                mock_cursor = MagicMock()

                def mogrify_side_effect(sql, args):
                    return b"INSERT INTO aircraft_states ..."

                mock_cursor.mogrify = MagicMock(side_effect=mogrify_side_effect)

                mock_conn = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_connect.return_value = mock_conn

                yield mock_cursor, mock_conn, mock_connect

    @pytest.mark.parametrize(
        "countries,aircraft,expected_result",
        [
            # Тест 1: Обычный случай (1 страна)
            (
                {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"]},
                {
                    "Ireland": [
                        [
                            "abc123",
                            "FL123",
                            "Ireland",
                            123,
                            123,
                            53.5,
                            -7.5,
                            10000.0,
                            False,
                            300.0,
                            280.0,
                            10.0,
                            None,
                            10000.0,
                            "1234",
                            False,
                            1,
                            1,
                        ]
                    ]
                },
                1,
            ),
            # Тест 2: Пустые данные о самолетах (1 страна)
            ({"Ireland": ["53.0", "54.0", "-8.0", "-7.0"]}, {"Ireland": []}, 0),
            # Тест 3: Страна без координат
            (
                {"Unknown": []},
                {
                    "Unknown": [
                        ["def456", "FL456", "Unknown", 123, 123, 0, 0, 0, False, 0, 0, 0, None, 0, "0000", False, 1, 1]
                    ]
                },
                0,
            ),
            # Тест 4: None в данных (1 страна)
            (
                {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"]},
                {
                    "Ireland": [
                        None,
                        [
                            "abc123",
                            "FL123",
                            "Ireland",
                            123,
                            123,
                            53.5,
                            -7.5,
                            10000.0,
                            False,
                            300.0,
                            280.0,
                            10.0,
                            None,
                            10000.0,
                            "1234",
                            False,
                            1,
                            1,
                        ],
                    ]
                },
                1,
            ),
            # Тест 5: Несколько стран (2 страны)
            (
                {"Ireland": ["53.0", "54.0", "-8.0", "-7.0"], "UK": ["50.0", "51.0", "-1.0", "0.0"]},
                {
                    "Ireland": [
                        [
                            "abc123",
                            "FL123",
                            "Ireland",
                            123,
                            123,
                            53.5,
                            -7.5,
                            10000.0,
                            False,
                            300.0,
                            280.0,
                            10.0,
                            None,
                            10000.0,
                            "1234",
                            False,
                            1,
                            1,
                        ]
                    ],
                    "UK": [
                        [
                            "def456",
                            "FL456",
                            "UK",
                            456,
                            456,
                            50.5,
                            -0.5,
                            15000.0,
                            True,
                            450.0,
                            290.0,
                            5.0,
                            None,
                            15000.0,
                            "5678",
                            True,
                            2,
                            2,
                        ]
                    ],
                },
                2,
            ),
        ],
    )
    def test_save_data_various_cases(self, mock_db, countries, aircraft, expected_result):
        """Параметризованный тест различных случаев сохранения данных"""
        mock_cursor, mock_conn, mock_connect = mock_db

        # Настройка fetchone для каждой страны
        # Для каждой страны нужно 2 значения: проверка существования и ID
        fetchone_values = []
        for _ in countries:
            fetchone_values.extend([None, [1]])

        def fetchone_side_effect():
            values = list(fetchone_values)

            def inner():
                if values:
                    return values.pop(0)
                return None

            return inner

        mock_cursor.fetchone.side_effect = fetchone_side_effect()

        result = save_data_to_db(countries, aircraft, "test_db")

        assert isinstance(result, int)
        assert result == expected_result, f"Ожидалось {expected_result}, получено {result}"
        mock_conn.commit.assert_called()
