# Курсовая работа: Мониторинг воздушных судов

## Описание проекта
Данный проект представляет собой систему для отслеживания воздушных судов в воздушном пространстве различных стран с использованием открытых API. Проект позволяет получать актуальные данные о самолетах, находящихся в воздухе, и сохранять их в базу данных PostgreSQL для дальнейшего анализа.

## Установка и настройка

## Установка и настройка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd coursework
```
## Установка зависимостей
```bash
pip install -r requirements.txt
```
## Настройка базы данных PostgreSQL
Создайте базу данных и настройте подключение в файле config.py:
```
python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aircraft_monitor',
    'user': 'your_username',
    'password': 'your_password'
}
```
4. Настройка стран для мониторинга

### Структура базы данных
# Таблица countries

id SERIAL PRIMARY KEY	Уникальный идентификатор
name VARCHAR(100)	Название страны
iso_code VARCHAR(10)	Код страны (ISO)
bounding box []	Географические координаты bounding box страны
created_at	TIMESTAMP WITH TIME ZONE DEFAULT NOW()	Время создания записи

# Таблица aircrafts_states

Поле	Тип   	Описание
iПоле	Тип	Описание
id	BIGSERIAL PRIMARY KEY	Уникальный идентификатор
icao24	VARCHAR(10) NOT NULL	ICAO-адрес самолета
callsign	VARCHAR(10)	Позывной
origin_country	VARCHAR(255) NOT NULL	Страна происхождения
time_position	INTEGER	Время позиции (timestamp)
last_contact	INTEGER NOT NULL	Время последнего контакта (timestamp)
longitude	FLOAT	Долгота
latitude	FLOAT	Широта
baro_altitude	FLOAT	Барометрическая высота
on_ground	BOOLEAN	На земле
velocity	FLOAT	Скорость (м/с)
true_track	FLOAT	Истинный курс
vertical_rate	FLOAT	Вертикальная скорость
geo_altitude	FLOAT	Геодезическая высота
squawk	VARCHAR(10)	Код Squawk
spi	BOOLEAN	SPI (Special Position Indicator)
position_source	INTEGER	Источник позиции
category	INTEGER	Категория воздушного судна
country_id	INTEGER REFERENCES countries(id) ON DELETE SET NULL	Внешний ключ к таблице countries
retrieved_at	TIMESTAMP WITH TIME ZONE DEFAULT NOW()	Время получения записи

## Модули проекта
# API модули (api)
1. BaseApi (базовый класс)
Предоставляет базовые методы для запросов
get_response() - выполняет GET-запрос и возвращает ответ
get_data()- возвращает данные в виде списка словарей
2. ApiBBox (координаты стран)
Получает географические координаты стран через Nominatim API
Возвращает bounding box для каждой страны
3. ApiAircrafts (данные о самолетах)
Получает данные о самолетах через OpenSky Network API
Фильтрует самолеты по bounding box стран


2. Утилиты (utils)
Функция get_all_data()
Преобразует сырые данные из API в структурированный формат
Подготавливает данные для загрузки в PostgreSQL


3. База данных (dbcreator)
DBCreator
Класс для создания и настройки базы данных:
Метод: create_database()
Создает таблицы в PostgreSQL
Устанавливает внешние ключи и индексы
Метод: save_data_to_db()
Выполняет загрузку данных

4. Менеджер для работы с базой данных (dbmanager)
DBManager
Основной класс для работы с данными:

Метод	Описание
get_countries_and_aeroplanes_count()	Получает список всех стран и количество самолетов в их воздушном пространстве
get_all_aeroplanes()	Получает список всех воздушных судов
get_avg_speed()	Вычисляет среднюю скорость всех самолетов
get_aeroplanes_with_higher_speed()	Возвращает самолеты со скоростью выше средней
get_aeroplanes_with_keyword(keyword)	Ищет самолеты по ключевому слову в позывном (например, 'ACA' для Air Canada)

4. Логирование (logging)
Logger
Настройка логирования для всех модулей
Сохранение логов в файл 
Уровни логирования: DEBUG, INFO, WARNING, ERROR

Использование
Запуск основной программы
```bash
python main.py
```