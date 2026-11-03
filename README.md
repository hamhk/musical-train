# depviz — визуализация графа зависимостей npm

Только стандартная библиотека Python 3.8+. Зависимости читаются напрямую из реестра npm по HTTP.

## Запуск
```
python main.py -p express --show-config            # этап 1: параметры
python main.py -p express --direct                 # этап 2: прямые зависимости
python main.py -p A -t -r examples/cycle.txt -a    # этап 3: тестовый репозиторий, циклы
python main.py -p express --load-order             # этап 4: порядок загрузки
python main.py -p express -a -o express.png        # этап 5: Mermaid + PNG + ASCII-дерево
```
Опции: `-p` пакет, `--package-version`, `-r` URL/файл, `-t` тестовый режим, `-o` PNG, `-a` ASCII-дерево,
`--show-config`, `--direct`, `--load-order`, `--no-image`.

Формат тестового репозитория (`examples/*.txt`): `A: B C`, пакеты — заглавные латинские буквы.

PNG строится из Mermaid-текста: локальным `mmdc` (если установлен) или сервисом mermaid.ink.
Рядом с PNG сохраняется `.mmd`.

## Git
`sh init_repo.sh https://github.com/ЛОГИН/РЕПО.git` — 5 коммитов по этапам и push.

## Тесты
`python -m unittest discover -s tests`

## Сравнение с npm (этапы 4 и 5)
```
npm view express dependencies
npm ls --all            # дерево; сравнить с -a
npm install --dry-run   # состав устанавливаемых пакетов
```
Возможные расхождения: npm ставит `optionalDependencies` и `peerDependencies` (npm ≥ 7), а depviz читает
только `dependencies`; npm хранит несколько версий одного пакета (по узлу на версию) и «поднимает» (hoist)
общие зависимости, а depviz идентифицирует узел по имени и берёт первую разрешённую версию; npm не
гарантирует строгий порядок загрузки (параллельная установка, порядок задаёт lock-файл), depviz даёт
топологический порядок (зависимости раньше зависимых); разрешение диапазонов — упрощённая
реализация semver (без пререлизов).
