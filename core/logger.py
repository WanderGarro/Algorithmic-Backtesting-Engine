import logging
from time import time
from sys import stdout

class Logger:
    """
    Универсальный класс для настройки и управления логированием в проекте.

    Предоставляет гибкую систему логирования с поддержкой различных обработчиков,
    форматирования с иконками. Особенно ориентирован на корректную работу в Docker-окружении.

    Основные возможности:
        Вывод логов в консоль с форматированием и иконками
        Поддержка различных уровней логирования (DEBUG, INFO, ERROR и др.)
        Интеграция с Docker (логи направляются в stdout)
        Unicode-иконки для различных уровней логирования
        На русском языке названия уровней логирования
        Предотвращение дублирования обработчиков

    Атрибуты класса:
        _LEVEL_ICONS (dict): Соответствие уровней логирования иконкам в Unicode
        _LEVEL_NAMES (dict): На русском языке названия уровней логирования
        _MAX_MESSAGES_PER_MINUTE(int): Максимальное количество сообщений в минуту

    Аргументы:
        name (str): Имя логгера (обычно передается __name__ вызывающего модуля)
        level (int, optional): Уровень логирования из модуля logging. По умолчанию: logging.INFO

    Применение:
        В Docker-окружении логи автоматически направляются в stdout,
        что позволяет использовать `docker logs` для просмотра логов.

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

    # Максимальное количество сообщений в минуту
    _MAX_MESSAGES_PER_MINUTE = 10000

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Инициализирует логгер с указанным именем и уровнем логирования.

        Создает новый логгер или возвращает существующий с тем же именем.
        Предотвращает дублирование обработчиков при повторной инициализации.

        Аргументы:
            name (str): Имя логгера (обычно __name__ вызывающего модуля)
            level (int): Уровень логирования из модуля logging

        Применение:
            Если логгер с указанным именем уже существует и имеет обработчики,
            новые обработчики добавлены не будут (предотвращение дублирования).
        """
        # Инициализация
        self._message_count = 0
        self._last_reset = time()
        self.logger = logging.getLogger(name)

        # Предотвращаем добавление обработчиков несколько раз
        if not self.logger.handlers:
            self.logger.setLevel(level)
            self.logger.propagate = False
            self._setup_docker_handlers()

    def _setup_docker_handlers(self) -> None:
        """
        Настраивает обработчики логирования для Docker-окружения.

        В Docker-контейнерах рекомендуется направлять логи в stdout/stderr,
        чтобы они могли быть перехвачены системой логирования Docker и
        доступны через команды `docker logs` и системы мониторинга.

        Создает и настраивает:
            Formatter с временными метками и структурой логов
            StreamHandler для вывода в стандартный поток вывода (stdout)

        Формат логов:
            YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message.

        Возвращает:
            None
        """

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # Обработчик для консоли
        console_handler = logging.StreamHandler(stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(self._rate_limit_filter)

        # Обработчик для файла - исправленный путь
        file_handler = logging.FileHandler('/app/logs/log.log')
        file_handler.setFormatter(formatter)
        file_handler.addFilter(self._rate_limit_filter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def _rate_limit_filter(self, record) -> bool:
        """
        Фильтр для ограничения частоты логирования.

        Обеспечивает защиту от чрезмерно частого логирования, которое может привести к:
            Переполнению лог-файлов
            Избыточной нагрузке на систему
            Сложностям анализа логов при слишком большом объеме данных

        Принцип работы:
            Подсчитывает количество сообщений за текущую минуту
            При превышении лимита (_MAX_MESSAGES_PER_MINUTE) блокирует новые сообщения
            Каждую минуту счетчик сбрасывается
            При первом превышении лимита выводится однократное предупреждение

        Алгоритм:
            1. Получает текущее время
            2. Проверяет, прошла ли минута с последнего сброса:
                Если да: сбрасывает счетчик сообщений и обновляет время сброса
            3. Проверяет превышение лимита:
                Если лимит превышен:
                   * При ПЕРВОМ превышении выводит предупреждение.
                   * Увеличивает счетчик и возвращает False (сообщение не логируется).
                Если лимит не превышен:
                   * Увеличивает счетчик и возвращает True (сообщение логируется)

        Особенности:
            Использует logging.warning вместо self.logger для избежания рекурсии
            Предупреждение выводится только один раз при первом превышении лимита
            Фильтр применяется ко ВСЕМ сообщениям логгера

        Аргументы:
            record: Объект записи лога, содержащий информацию о сообщении

        Возвращает (bool): True: сообщение должно быть обработано (не превышен лимит)
                           False: сообщение должно быть отброшено (превышен лимит)

        Пример работы:
            Лимит: 1000 сообщений/минуту
                Сообщения 1-1000: проходят нормально
                Сообщение 1001: выводится предупреждение и сообщение блокируется
                Сообщения 1002-...: блокируются без предупреждений
                Через 60+ секунд: счетчик сбрасывается, цикл повторяется

        Применение:
            Фильтр автоматически добавляется ко всем обработчикам логгера
            при инициализации через _setup_docker_handlers()
        """
        current_time = time()

        # Сбрасываем счетчик каждую минуту
        if current_time - self._last_reset > 60:
            self._message_count = 0
            self._last_reset = current_time

        # Проверяем лимит
        if self._message_count >= self._MAX_MESSAGES_PER_MINUTE:
            if self._message_count == self._MAX_MESSAGES_PER_MINUTE:
                # Однократное предупреждение о превышении лимита
                logging.warning("Достигнут лимит сообщений в минуту, логирование приостановлено")
            self._message_count += 1
            return False

        self._message_count += 1
        return True

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