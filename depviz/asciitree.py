"""ASCII-дерево зависимостей."""


def render_tree(graph):
    lines = [graph.labels[graph.root]]
    expanded = set()

    def walk(node, prefix, path):
        expanded.add(node)
        deps = graph.edges.get(node, [])
        for i, dep in enumerate(deps):
            last = i == len(deps) - 1
            branch = "└── " if last else "├── "
            mark = ""
            if dep in path:
                mark = " (цикл)"
            elif dep in expanded and graph.edges.get(dep):
                mark = " (уже показан выше)"
            lines.append(f"{prefix}{branch}{graph.labels[dep]}{mark}")
            if not mark:
                walk(dep, prefix + ("    " if last else "│   "), path | {dep})

    walk(graph.root, "", {graph.root})
    return "\n".join(lines)
