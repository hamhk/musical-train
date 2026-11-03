"""Этап 4. Порядок загрузки: зависимости раньше зависящих (постпорядок DFS)."""


def load_order(graph):
    order, seen = [], set()

    def visit(node):
        seen.add(node)
        for dep in graph.edges.get(node, []):
            if dep not in seen:   # обратные рёбра циклов пропускаются автоматически
                visit(dep)
        order.append(node)

    visit(graph.root)
    return order
