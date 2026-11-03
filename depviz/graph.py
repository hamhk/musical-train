"""Этап 3. Построение графа зависимостей рекурсивным DFS с обработкой циклов."""
import sys

_VISITING = 1


class DependencyGraph:
    def __init__(self, root):
        self.root = root
        self.edges = {}          # имя -> список зависимостей (в порядке обнаружения)
        self.cycles = []         # найденные циклы: списки вида [A, B, C, A]
        self.back_edges = set()  # рёбра, замыкающие цикл
        self.labels = {}


def build_graph(root, repo):
    """repo.direct_dependencies(name) -> list[str]; repo.label(name) -> str."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))
    g = DependencyGraph(root)
    state = {}
    stack = []

    def dfs(node):
        state[node] = _VISITING
        stack.append(node)
        deps = repo.direct_dependencies(node)
        g.edges[node] = deps
        g.labels[node] = repo.label(node)
        for dep in deps:
            st = state.get(dep)
            if st == _VISITING:  # обратное ребро -> цикл
                g.back_edges.add((node, dep))
                g.cycles.append(stack[stack.index(dep):] + [dep])
            elif st is None:
                dfs(dep)
        stack.pop()
        state[node] = 2  # завершён

    dfs(root)
    for deps in list(g.edges.values()):
        for d in deps:
            g.labels.setdefault(d, d)
    return g
