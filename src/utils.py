import logging
from datetime import datetime
from pathlib import Path

from src.api import ApiAircrafts
from src.api import ApiBBox
from src.logger import Logger

project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)
log_filename = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

Logger.configure(
    console_output=False,
    level=logging.DEBUG,
    log_file=str(log_filename),
    format_str="%(asctime)s - %(funcName)s - %(pathname)s - %(levelname)s - %(message)s",
)


log = Logger(__name__)


def get_all_data():
    """Получает все данные в одном запросе для последующего формирования базы данных."""

    api = ApiBBox()
    data = api.get_data()
    countries = api.countries
    api_air = ApiAircrafts(data)
    aircraft_data = api_air.get_data()

    countries_data = dict(zip(countries, data))

    states_list = [item["states"] for item in aircraft_data]
    aircrafts_data = dict(zip(countries, states_list))

    call_signs = [plane[1].strip()[:3] for region in states_list for plane in region if plane[1].strip()]
    log.info("Получены данные по странам")
    log.info("Получены позывные сигналы")
    return countries_data, aircrafts_data, call_signs
