import logging
import sys
from typing import Optional


class Logger:
    """
    Класс для логирования.
    Каждый экземпляр соответствует отдельному логгеру с именем (__name__ модуля).
    Настройка форматирования и обработчиков производится однократно через метод configure().
    """

    _configured = False

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        console_output: bool = True,
    ):
        if cls._configured:
            return
        cls._configured = True

        # Очищаем существующие обработчики
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.root.setLevel(level)

        # Создаем форматтер
        formatter = logging.Formatter(format_str)

        # Добавляем обработчики
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logging.root.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logging.root.addHandler(file_handler)

        if not logging.root.handlers:
            logging.root.addHandler(logging.NullHandler())

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def set_level(self, level: int):
        self.logger.setLevel(level)

    def get_logger(self):
        return self.logger
