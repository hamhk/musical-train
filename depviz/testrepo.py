"""Тестовый репозиторий: текстовый файл, пакеты — заглавные латинские буквы.

Формат строки:   A: B C        (A зависит от B и C)
                 D:            (нет зависимостей)
Строки, начинающиеся с '#', и пустые строки игнорируются.
"""
import re

from .errors import RepositoryError

_NAME = re.compile(r"^[A-Z]+$")


class TestRepository:
    __test__ = False  # чтобы pytest не принимал класс за тест

    def __init__(self, path):
        self.graph = {}
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            raise RepositoryError(f"не удалось прочитать {path}: {e.strerror}")
        except UnicodeDecodeError:
            raise RepositoryError(f"файл {path} не в кодировке UTF-8")
        for n, line in enumerate(lines, 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if ":" not in line:
                raise RepositoryError(f"{path}:{n}: ожидается формат 'A: B C', получено {line!r}")
            name, deps = line.split(":", 1)
            name = name.strip()
            deps = deps.split()
            for x in [name] + deps:
                if not _NAME.match(x):
                    raise RepositoryError(
                        f"{path}:{n}: имя {x!r} — должно состоять из заглавных латинских букв")
            if name in self.graph:
                raise RepositoryError(f"{path}:{n}: пакет {name} описан повторно")
            self.graph[name] = list(dict.fromkeys(deps))

    def direct_dependencies(self, name):
        # упомянутый, но не описанный пакет считаем листом; корень проверяется в cli
        return list(self.graph.get(name, []))

    def has(self, name):
        return name in self.graph

    def label(self, name):
        return name
