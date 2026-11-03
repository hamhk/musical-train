"""Этап 5. Текстовое представление графа на языке Mermaid."""


def to_mermaid(graph):
    ids = {name: f"n{i}" for i, name in enumerate(graph.labels)}
    out = ["graph TD"]
    for name, nid in ids.items():
        label = graph.labels[name].replace('"', "&quot;")
        out.append(f'    {nid}["{label}"]')
    for name, deps in graph.edges.items():
        for d in deps:
            arrow = "-.->" if (name, d) in graph.back_edges else "-->"
            out.append(f"    {ids[name]} {arrow} {ids[d]}")
    return "\n".join(out) + "\n"
