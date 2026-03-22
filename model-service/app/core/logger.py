import logging


class AppLogger:
    """Единый логгер для всего приложения"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        self._initialized = True

    def get_logger(self, name: str) -> logging.Logger:
        """Получить логгер для модуля"""
        return self.logger.getChild(name)


app_logger = AppLogger()

def get_logger(name: str) -> logging.Logger:
    """Получить логгер по имени модуля"""
    return app_logger.get_logger(name)