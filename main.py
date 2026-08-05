from datetime import datetime
from pathlib import Path
import logging
from src.dbcreator import create_database, save_data_to_db
from src.dbmanager import DBManager
from src.logger import Logger
from src.utils import get_all_data

project_root = Path(__file__).parent.resolve()
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

def main():
    log.info("Программа запущена")
    print("Программа для создания базы данных по воздушным судам в пространстве")
    while True:
        print("Введите 1 для создания базы данных")
        print("Введите 2 для выхода")
        choice = input("Введите номер: ")
        if choice == '1':
            database_name = "aircraft_db"
            create_database(database_name)
            countries_data, aircrafts_data, call_signs = get_all_data()
            save_data_to_db(countries_data, aircrafts_data)
            log.info(f"База данных {database_name} создана")
            db = DBManager()
            print("База данных создана")
            print("Для работы с базой данных введите: ")
            print("1 - для вывода списка всех стран и количества самолетов")
            print("2 - для вывода списка всех самолетов")
            print("3 - для получения значения средней скорости по самолетам")
            print("4 - для получения списка всех самолетов, у которых скорость выше средней")
            print("5 - для получения списка всех самолетов, с заданным позывным")
            print("6 - выход")
            while True:
                choice = input("Введите номер: ")
                if choice == '1':
                    result = db.get_countries_and_aeroplanes_count()
                    for country, count in result:
                        print(f" В воздушном пространстве страны: {country}")
                        print(f"Количество самолетов: {count}")
                elif choice == '2':
                    all_planes = db.get_all_aeroplanes()
                    for plane in all_planes:
                        print(f"Самолет :{plane}")
                elif choice == '3':
                    average_speed = db.get_avg_speed()
                    print(f"Средняя скорость самолетов из базы данных: {average_speed}")
                elif choice == '4':
                    result = db.get_aeroplanes_with_lower_speed()
                    for r in result:
                        print(f" Самолет: {r}")
                elif choice == '5':
                    call_sign = input("Введите позывной: ")
                    print("Например: ACA")
                    result = db.get_aeroplanes_with_keyword(call_sign)
                    print(f"Самолеты с позывным {call_sign}: {(row for row in result)}")
                elif choice == '6':
                    exit()
                else:
                    print("Неверный выбор")
                    continue

            break
        elif choice == '2':
            log.info("Программа завершена")
            print("Программа завершена")
            break
        else:
            print("Неверный выбор")
            continue

if __name__ == "__main__":
    main()