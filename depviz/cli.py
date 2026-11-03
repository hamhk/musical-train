import os
import sys

from .config import parse_config
from .errors import DepVizError, RepositoryError


def _make_repo(cfg):
    if cfg.test_mode:
        from .testrepo import TestRepository
        repo = TestRepository(cfg.repo)
        if not repo.has(cfg.package):
            raise RepositoryError(f"пакет {cfg.package} не описан в файле {cfg.repo}")
        return repo
    from .npm import NpmRepository
    return NpmRepository(cfg.repo, cfg.package, cfg.package_version)


def run(argv=None):
    cfg = parse_config(argv)

    if cfg.show_config:                                   # этап 1
        for k, v in cfg.as_pairs():
            print(f"{k}: {v}")
        print()

    repo = _make_repo(cfg)

    if cfg.direct:                                        # этап 2
        deps = repo.direct_dependencies(cfg.package)
        print(f"Прямые зависимости {repo.label(cfg.package)}:")
        for d in deps:
            print(f"  {d}")
        if not deps:
            print("  (нет)")
        return 0

    from .graph import build_graph                        # этап 3
    graph = build_graph(cfg.package, repo)
    print(f"Узлов в графе: {len(graph.labels)}, "
          f"рёбер: {sum(len(v) for v in graph.edges.values())}")
    for cyc in graph.cycles:
        print("Обнаружен цикл: " + " -> ".join(cyc))

    if cfg.load_order:                                    # этап 4
        from .loadorder import load_order
        print("\nПорядок загрузки:")
        for i, n in enumerate(load_order(graph), 1):
            print(f"  {i}. {graph.labels[n]}")

    if cfg.ascii_tree:                                    # этап 5
        from .asciitree import render_tree
        print("\n" + render_tree(graph))

    from .mermaid import to_mermaid
    text = to_mermaid(graph)
    mmd_path = os.path.splitext(cfg.output)[0] + ".mmd"
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nMermaid-описание сохранено: {mmd_path}")

    if not cfg.no_image:
        from .render import render_png
        render_png(text, cfg.output)
        print(f"Изображение графа сохранено: {cfg.output}")
    return 0


def main(argv=None):
    try:
        return run(argv)
    except DepVizError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
