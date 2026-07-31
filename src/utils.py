from src.api import ApiBBox,ApiAircrafts


def get_all_data():
    """Получает все данные в одном запросе для последующего формирования базы данных."""

    api = ApiBBox()
    data = api.get_data()
    countries = api.countries
    api_air = ApiAircrafts(data)
    aircraft_data = api_air.get_data()

    countries_data = dict(zip(countries, data))

    states_list = [item['states'] for item in aircraft_data]
    aircrafts_data = dict(zip(countries, states_list))

    call_signs = [
        plane[1].strip()[:3]
        for region in states_list
        for plane in region
        if plane[1].strip()
    ]

    return countries_data, aircrafts_data, call_signs


if __name__ == '__main__':
    countries_data, aircrafts_data, call_signs = get_all_data()

    print("Данные по странам:")
    print(countries_data)
    print("\nДанные по самолетам:")
    print(aircrafts_data)
    print("\nПозывные сигналы:")
    print(call_signs)