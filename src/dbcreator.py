import psycopg2
from psycopg2.extras import execute_batch

from src.config import config
from src.utils import get_all_data


def create_database(database_name: str):
    """Создание базы данных и таблиц для сохранения данных о странах и самолетах"""
    params = config()
    params = {k: str(v).encode('ascii', 'ignore').decode('ascii') for k, v in params.items()}
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
    exists = cur.fetchone()

    if exists:
        cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid()
        """, (database_name,))

        cur.execute(f"DROP DATABASE {database_name}")
        print(f"База данных {database_name} удалена")

    cur.execute(f"CREATE DATABASE {database_name}")
    print(f"База данных {database_name} создана")

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                iso_code VARCHAR(10),
                bounding_box FLOAT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE aircraft_states (
                id BIGSERIAL PRIMARY KEY,
                icao24 VARCHAR(10) NOT NULL,
                callsign VARCHAR(10),
                origin_country VARCHAR(255) NOT NULL,
                time_position INTEGER,
                last_contact INTEGER NOT NULL,
                longitude FLOAT,
                latitude FLOAT,
                baro_altitude FLOAT,
                on_ground BOOLEAN,
                velocity FLOAT,
                true_track FLOAT,
                vertical_rate FLOAT,
                geo_altitude FLOAT,
                squawk VARCHAR(10),
                spi BOOLEAN,
                position_source INTEGER,
                category INTEGER,
                country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
                retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)

    conn.commit()
    conn.close()
    print("Таблицы успешно созданы")


def save_data_to_db(countries_data, aircraft_data, database_name='aircraft_db'):
    """Сохранение данных о странах и самолетах в базу данных."""


    params = config()
    params = {k: str(v).encode('ascii', 'ignore').decode('ascii') for k, v in params.items()}

    conn = None
    cur = None

    try:
        conn = psycopg2.connect(dbname=database_name, **params)
        cur = conn.cursor()

        country_ids = {}

        for country_name, bbox in countries_data.items():
            if not bbox or len(bbox) < 4:
                print(f"Пропускаем {country_name}: нет координат")
                continue

            bbox_float = [
                float(bbox[2]),
                float(bbox[0]),
                float(bbox[3]),
                float(bbox[1])
            ]

            cur.execute("SELECT id FROM countries WHERE name = %s", (country_name,))
            existing = cur.fetchone()

            if existing:
                country_id = existing[0]
                cur.execute("""
                    UPDATE countries 
                    SET bounding_box = %s, updated_at = NOW() 
                    WHERE id = %s
                """, (bbox_float, country_id))
                print(f"Обновлена: {country_name}")
            else:
                cur.execute("""
                    INSERT INTO countries (name, bounding_box) 
                    VALUES (%s, %s) 
                    RETURNING id
                """, (country_name, bbox_float))
                country_id = cur.fetchone()[0]
                print(f"Добавлена: {country_name}")

            country_ids[country_name] = country_id

        conn.commit()
        print(f"Сохранено стран: {len(country_ids)}")

        insert_query = """
            INSERT INTO aircraft_states (
                icao24, callsign, origin_country, time_position, last_contact,
                longitude, latitude, baro_altitude, on_ground, velocity,
                true_track, vertical_rate, geo_altitude, squawk, spi,
                position_source, category, country_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        total_saved = 0

        for country_name, states in aircraft_data.items():
            if country_name not in country_ids:
                print(f"Страна {country_name} не найдена, пропускаем")
                continue

            country_id = country_ids[country_name]
            states_to_insert = []

            for state in states:
                if not state:
                    continue

                icao24 = state[0] if len(state) > 0 else None
                callsign = state[1].strip() if len(state) > 1 and state[1] else None
                origin_country = state[2] if len(state) > 2 else None
                time_position = state[3] if len(state) > 3 else None
                last_contact = state[4] if len(state) > 4 else None
                longitude = state[5] if len(state) > 5 else None
                latitude = state[6] if len(state) > 6 else None
                baro_altitude = state[7] if len(state) > 7 else None
                on_ground = state[8] if len(state) > 8 else None
                velocity = state[9] if len(state) > 9 else None
                true_track = state[10] if len(state) > 10 else None
                vertical_rate = state[11] if len(state) > 11 else None
                geo_altitude = state[13] if len(state) > 13 else None
                squawk = state[14] if len(state) > 14 else None
                spi = state[15] if len(state) > 15 else None
                position_source = state[16] if len(state) > 16 else None
                category = state[17] if len(state) > 17 else None

                states_to_insert.append((
                    icao24, callsign, origin_country, time_position, last_contact,
                    longitude, latitude, baro_altitude, on_ground, velocity,
                    true_track, vertical_rate, geo_altitude, squawk, spi,
                    position_source, category, country_id
                ))

            if states_to_insert:
                execute_batch(cur, insert_query, states_to_insert)
                total_saved += len(states_to_insert)
                print(f"{country_name}: сохранено {len(states_to_insert)} самолетов")

        conn.commit()
        print(f"Всего сохранено: {total_saved} записей")
        return total_saved

    except psycopg2.Error as e:
        print(f"Ошибка: {e}")
        if conn:
            conn.rollback()
        return 0

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    create_database("aircraft_db")
    print("Database and tables created successfully")

    countries_data, aircrafts_data, call_signs = get_all_data()

    print(f"\nПолучено {len(countries_data)} стран и данные о самолетах")
    saved_count = save_data_to_db(countries_data, aircrafts_data, "aircraft_db")

    print(f"\nДанные сохранены в базу данных. Сохранено {saved_count} записей")
