import psycopg2
from src.config import config


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
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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


if __name__ == '__main__':
    create_database("aircraft_db")
    print("Database and tables created successfully")