import psycopg2
import os
from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from datetime import datetime
from src.logger import Logger

load_dotenv()

project_root = Path(__file__).parent.parent
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


class DBManager:
    """Класс для работы с информацией из базы данных"""
    def __init__(self, dbname="aircraft_db"):
        """Инициализация менеджера базы данных"""
        self.dbname = dbname
        self.conn = None
        self.connect()

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=self.dbname,
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            log.info(f"Connected to database {self.dbname}")
        except psycopg2.Error as e:
            log.error(f"Error connecting to database: {e}")
            raise

    def get_countries_and_aeroplanes_count(self):
        """Получает список всех стран и количество самолетов"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT countries.name as country_name, COUNT(aircraft_states.id) as aircraft_count
            FROM countries 
            INNER JOIN aircraft_states ON countries.id = aircraft_states.country_id
            GROUP BY countries.name
            ORDER BY aircraft_count DESC
        """)
        log.info("Получен список всех стран и количество самолетов.")
        return cur.fetchall()

    def get_all_aeroplanes(self):
        """Получает список всех воздушных судов."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM aircraft_states")
        log.info("Получен список всех воздушных судов.")
        return cur.fetchall()

    def get_avg_speed(self):
        """Получает среднюю скорость по самолетам."""
        cur = self.conn.cursor()
        cur.execute("SELECT AVG(velocity) FROM aircraft_states")
        log.info("Получена средняя скорость по самолетам.")
        return cur.fetchone()[0]


    def get_aeroplanes_with_lower_speed(self):
        """Получает список всех самолетов, у которых скорость выше средней."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM aircraft_states WHERE velocity < (SELECT AVG(velocity) FROM aircraft_states)")
        log.info("Получен список всех самолетов, у которых скорость выше средней.")
        return cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str):
        """Получает список всех самолетов, в позывном которых содержатся переданные в метод символы."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM aircraft_states WHERE aircraft_states.callsign LIKE %s", (f"%{keyword}%",))
        log.info(f"Получен список всех самолетов, в позывном которых содержатся символы {keyword}.")
        return cur.fetchall()


if __name__ == '__main__':
    db = DBManager()
    velocity_avg = db.get_avg_speed()
    print(velocity_avg)
    results = db.get_countries_and_aeroplanes_count()
    res = db.get_aeroplanes_with_keyword('AAL')
    print(res)
    resul = db.get_aeroplanes_with_lower_speed()
    for r in resul:
        print(f" Самолет: {r}")
    for country, count in results:
        print(f"{country}: {count} aircraft")
    all_planes = db.get_all_aeroplanes()
    for plane in all_planes:
        print(plane)