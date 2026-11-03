class DepVizError(Exception):
    """Базовая ошибка приложения: сообщение показывается пользователю."""


class ConfigError(DepVizError):
    """Некорректные параметры командной строки."""


class RepositoryError(DepVizError):
    """Ошибка чтения репозитория (сеть, формат файла, пакет не найден)."""
