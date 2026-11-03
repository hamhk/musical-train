"""Этап 2. Получение прямых зависимостей npm-пакета напрямую из реестра (HTTP)."""
import json
import urllib.error
import urllib.request
from urllib.parse import quote

from .errors import RepositoryError
from .semver import max_satisfying


class NpmRepository:
    """Провайдер зависимостей: узлы графа — имена пакетов."""

    def __init__(self, registry_url, root, root_spec=None, timeout=20):
        self.registry = registry_url.rstrip("/")
        self.timeout = timeout
        self._packuments = {}
        self.specs = {root: root_spec or "latest"}
        self.versions = {}

    def _packument(self, name):
        if name not in self._packuments:
            url = f"{self.registry}/{quote(name, safe='@')}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    self._packuments[name] = json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise RepositoryError(f"пакет {name!r} не найден в репозитории {self.registry}")
                raise RepositoryError(f"HTTP {e.code} при запросе {url}")
            except urllib.error.URLError as e:
                raise RepositoryError(f"не удалось подключиться к {url}: {e.reason}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise RepositoryError(f"репозиторий вернул не JSON: {url}")
            except TimeoutError:
                raise RepositoryError(f"таймаут при запросе {url}")
        return self._packuments[name]

    def _resolve(self, name, spec):
        data = self._packument(name)
        versions = data.get("versions") or {}
        tags = data.get("dist-tags") or {}
        if not versions:
            raise RepositoryError(f"у пакета {name!r} нет версий")
        if spec in tags:
            chosen = tags[spec]
        else:
            chosen = max_satisfying(versions.keys(), spec)
            if chosen is None:  # нестандартный spec (git, alias, ...) — берём latest
                chosen = tags.get("latest") or max_satisfying(versions.keys(), "*")
        if chosen not in versions:
            raise RepositoryError(f"версия {spec!r} пакета {name!r} не найдена")
        return chosen, versions[chosen]

    def direct_dependencies(self, name):
        """Список имён прямых зависимостей (поле dependencies package.json)."""
        spec = self.specs.get(name, "latest")
        version, meta = self._resolve(name, spec)
        self.versions[name] = version
        deps = meta.get("dependencies") or {}
        for dep, dspec in deps.items():
            self.specs.setdefault(dep, dspec)
        return list(deps.keys())

    def label(self, name):
        v = self.versions.get(name)
        return f"{name}@{v}" if v else name
