"""Этап 1. Конфигурация из опций командной строки + валидация."""
import argparse
import os
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from .errors import ConfigError

DEFAULT_REGISTRY = "https://registry.npmjs.org"
NPM_NAME_RE = re.compile(r"^(?:@[a-z0-9][a-z0-9._~-]*/)?[a-z0-9][a-z0-9._~-]*$")
TEST_NAME_RE = re.compile(r"^[A-Z]+$")


@dataclass
class Config:
    package: str
    repo: str
    test_mode: bool
    output: str
    ascii_tree: bool
    package_version: Optional[str]
    show_config: bool
    direct: bool
    load_order: bool
    no_image: bool

    def as_pairs(self):
        return [
            ("package", self.package),
            ("package_version", self.package_version or "latest"),
            ("repo", self.repo),
            ("test_mode", self.test_mode),
            ("output", self.output),
            ("ascii_tree", self.ascii_tree),
        ]


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # вместо sys.exit(2) с usage — наше исключение
        raise ConfigError(message)


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(
        prog="depviz",
        description="Визуализация графа зависимостей npm-пакета.",
    )
    p.add_argument("-p", "--package", required=True, help="имя анализируемого пакета")
    p.add_argument("--package-version", default=None,
                   help="версия или диапазон (по умолчанию latest)")
    p.add_argument("-r", "--repo", default=None,
                   help=f"URL репозитория (по умолчанию {DEFAULT_REGISTRY}) "
                        "или путь к файлу тестового репозитория")
    p.add_argument("-t", "--test-mode", action="store_true",
                   help="работать с тестовым репозиторием (файл графа)")
    p.add_argument("-o", "--output", default="graph.png",
                   help="имя файла с изображением графа (.png)")
    p.add_argument("-a", "--ascii-tree", action="store_true",
                   help="вывести зависимости в виде ASCII-дерева")
    p.add_argument("--show-config", action="store_true",
                   help="вывести параметры в формате ключ-значение (этап 1)")
    p.add_argument("--direct", action="store_true",
                   help="вывести только прямые зависимости и выйти (этап 2)")
    p.add_argument("--load-order", action="store_true",
                   help="вывести порядок загрузки зависимостей (этап 4)")
    p.add_argument("--no-image", action="store_true",
                   help="не создавать PNG (сохранить только .mmd)")
    return p


def parse_config(argv=None) -> Config:
    args = build_parser().parse_args(argv)

    repo = args.repo
    if repo is None:
        if args.test_mode:
            raise ConfigError("в режиме --test-mode нужно указать --repo (путь к файлу)")
        repo = DEFAULT_REGISTRY

    package = args.package.strip()
    if not package:
        raise ConfigError("имя пакета не может быть пустым")

    if args.test_mode:
        if not TEST_NAME_RE.match(package):
            raise ConfigError(
                f"в тестовом режиме имя пакета — заглавные латинские буквы, получено: {package!r}")
        if not os.path.exists(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        if not os.path.isfile(repo):
            raise ConfigError(f"путь к тестовому репозиторию не является файлом: {repo}")
        if args.package_version:
            raise ConfigError("--package-version не используется в тестовом режиме")
    else:
        if not NPM_NAME_RE.match(package):
            raise ConfigError(f"некорректное имя npm-пакета: {package!r}")
        u = urlparse(repo)
        if u.scheme not in ("http", "https") or not u.netloc:
            raise ConfigError(
                f"некорректный URL репозитория: {repo!r} (ожидается http:// или https://). "
                "Для файла используйте --test-mode")
        repo = repo.rstrip("/")

    out = args.output
    if not out.lower().endswith(".png"):
        raise ConfigError(f"файл изображения должен иметь расширение .png: {out!r}")
    out_dir = os.path.dirname(os.path.abspath(out))
    if not os.path.isdir(out_dir):
        raise ConfigError(f"каталог для выходного файла не существует: {out_dir}")
    if os.path.isdir(out):
        raise ConfigError(f"выходной путь — каталог, а не файл: {out}")

    return Config(
        package=package, repo=repo, test_mode=args.test_mode, output=out,
        ascii_tree=args.ascii_tree, package_version=args.package_version,
        show_config=args.show_config, direct=args.direct,
        load_order=args.load_order, no_image=args.no_image,
    )
