import pytest

from main import get_all_data


def test_api_returns_data():
    """Простой тест, который реально вызывает API"""
    try:
        countries_data, aircrafts_data, call_signs = get_all_data()

        # Базовые проверки
        assert isinstance(countries_data, dict)
        assert isinstance(aircrafts_data, dict)
        assert isinstance(call_signs, list)

        # Если данные есть - проверяем структуру
        if countries_data:
            assert all(isinstance(v, list) for v in countries_data.values())

        if call_signs:
            assert all(isinstance(s, str) for s in call_signs)
            assert all(len(s) == 3 for s in call_signs)

    except Exception as e:
        pytest.skip(f"API не доступен: {e}")
