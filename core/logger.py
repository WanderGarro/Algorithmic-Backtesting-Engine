import logging
from datetime import datetime
from os import path, makedirs
from logging.handlers import RotatingFileHandler

class Logger:
    """Класс для настройки и управления логированием в проекте.

    Поддерживает:
        Запись логов в файл с ротацией (ограничение по размеру)
        Вывод логов в консоль
        Разные уровни логирования (DEBUG, INFO, ERROR и др.)
        Автоматическое создание папки для логов

    Аргументы:
        name (str): Имя логгера (обычно __name__ вызывающего модуля)
        level (int, optional): Уровень логирования. По умолчанию logging.INFO.
        log_dir (str, optional): Папка для логов. По умолчанию "logs".
        filename_prefix (str, optional): Префикс имени файла. По умолчанию "log".
        max_bytes (int, optional): Макс. размер файла (в байтах) перед ротацией. По умолчанию 5 МБ.
        backup_count (int, optional): Кол-во бэкап-файлов. По умолчанию 3.


    Пример:
        >>> logger = Logger(__name__, level=logging.DEBUG)
        >>> logger.info('Тестовое сообщение')
        2023-10-01 12:00:00 - __main__ - INFO - ℹ️ Информация: Тестовое сообщение
    """

    _LEVEL_ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }

    _LEVEL_NAMES = {
        'DEBUG': 'Отладка',
        'INFO': 'Информация',
        'WARNING': 'Предупреждение',
        'ERROR': 'Ошибка',
        'CRITICAL': 'Критическая ошибка'
    }

    def __init__(self, name: str, level: int = logging.INFO, log_dir: str = "logs", filename_prefix: str = "log",
                 max_bytes: int = 5 * 1024 * 1024, backup_count: int = 3):

        self.logger = logging.getLogger(name)

        # Предотвращаем добавление обработчиков несколько раз
        if not self.logger.handlers:
            self.logger.setLevel(level)
            self._setup_handlers(log_dir, filename_prefix, max_bytes, backup_count)

    @staticmethod
    def _generate_log_filename(log_dir: str, filename_prefix: str) -> str:
        """Генерирует уникальное имя файла с временной меткой.

        Аргументы:
            log_dir (str): Папка для логов
            filename_prefix (str): Префикс имени файла

        Возвращает:
            str: Полный путь к файлу логов
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.log"
        return path.join(log_dir, filename)

    def _setup_handlers(self, log_dir: str, filename_prefix: str,
                        max_bytes: int, backup_count: int) -> None:
        """Настраивает обработчики для файла и консоли.

        Аргументы:
            log_dir (str): Папка для логов
            filename_prefix (str): Префикс имени файла
            max_bytes (int): Макс. размер файла до ротации
            backup_count (int): Кол-во бэкап-файлов
        """

        # Получаем корень проекта (на один уровень выше текущего файла)
        project_root = path.abspath(path.join(path.dirname(__file__), '..'))

        # Формируем полный путь к папке логов
        log_dir_path = path.join(project_root, log_dir)

        # Создаем директорию для логов
        makedirs(log_dir_path, exist_ok=True)

        # Генерируем уникальное имя файла с временной меткой
        log_file_path = self._generate_log_filename(log_dir_path, filename_prefix)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # Чередующий файловый обработчик
        file_handler = RotatingFileHandler(log_file_path,maxBytes=max_bytes,backupCount=backup_count,encoding='utf-8')
        file_handler.setFormatter(formatter)

        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Логируем информацию о создании нового лог-файла
        self.logger.info(f"Создан новый лог-файл: {path.basename(log_file_path)}")

    def _format_message(self, level: str, message: str) -> str:
        """Форматирует сообщение с иконкой и уровнем.

        Аргументы:
            level (str): Уровень сообщения
            message (str): Текст сообщения
        """
        icon = self._LEVEL_ICONS.get(level, '')
        level_name = self._LEVEL_NAMES.get(level, level)
        return f'{icon} {level_name}: {message}'

    def debug(self, message: str) -> None:
        """Логирует сообщение уровня DEBUG.

        Аргументы:
            message (str): Текст сообщения
        """
        self.logger.debug(self._format_message('DEBUG', message))

    def info(self, message: str) -> None:
        """Логирует сообщение уровня INFO.

        Аргументы:
            message (str): Текст сообщения
        """
        self.logger.info(self._format_message('INFO', message))

    def warning(self, message: str) -> None:
        """Логирует сообщение уровня WARNING.

        Аргументы:
            message (str): Текст сообщения
        """
        self.logger.warning(self._format_message('WARNING', message))

    def error(self, message: str, info: bool = False) -> None:
        """Логирует сообщение уровня ERROR.

        Аргументы:
            message (str): Текст сообщения
            info (bool, optional): Если True, добавляет traceback. По умолчанию False
        """
        self.logger.error(self._format_message('ERROR', message), exc_info=info)

    def critical(self, message: str, info: bool = False) -> None:
        """Логирует сообщение уровня CRITICAL.

        Аргументы:
            message (str): Текст сообщения
            info (bool, optional): Если True, добавляет traceback. По умолчанию False
        """
        self.logger.critical(self._format_message('CRITICAL', message), exc_info=info)