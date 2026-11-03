"""Минимальный разрешатель npm-диапазонов версий (без внешних библиотек)."""
import re

_FULL = re.compile(r"^(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$")
_PART = re.compile(
    r"^[v=]?(\d+|[xX*])?(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def parse_version(s):
    """'1.2.3' -> (1,2,3); версии с пререлизом -> None."""
    m = _FULL.match(s)
    if not m or m.group(4):
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _partial(s):
    m = _PART.match(s)
    if not m:
        raise ValueError(s)
    return tuple(int(g) if g is not None and g.isdigit() else None for g in m.groups())


def _comparator(tok):
    if tok in ("", "*", "x", "X", "latest"):
        return lambda v: True
    m = re.match(r"^(\^|~|>=|<=|>|<|=)?(.*)$", tok)
    op, rest = m.group(1), m.group(2)
    M, mi, pa = _partial(rest)
    if M is None:
        return lambda v: True
    lo = (M, mi or 0, pa or 0)
    if op == "^":
        if M > 0:
            hi = (M + 1, 0, 0)
        elif mi is None:
            hi = (1, 0, 0)
        elif mi > 0:
            hi = (0, mi + 1, 0)
        elif pa is None:
            hi = (0, 1, 0)
        else:
            hi = (0, 0, pa + 1)
        return lambda v: lo <= v < hi
    if op == "~":
        hi = (M + 1, 0, 0) if mi is None else (M, mi + 1, 0)
        return lambda v: lo <= v < hi
    if op in (None, "="):
        if mi is None:
            hi = (M + 1, 0, 0)
        elif pa is None:
            hi = (M, mi + 1, 0)
        else:
            return lambda v: v == lo
        return lambda v: lo <= v < hi
    if op == ">=":
        return lambda v: v >= lo
    if op == ">":
        if mi is None:
            return lambda v: v >= (M + 1, 0, 0)
        if pa is None:
            return lambda v: v >= (M, mi + 1, 0)
        return lambda v: v > lo
    if op == "<=":
        if mi is None:
            return lambda v: v < (M + 1, 0, 0)
        if pa is None:
            return lambda v: v < (M, mi + 1, 0)
        return lambda v: v <= lo
    return lambda v: v < lo  # "<"


def _range_predicate(part):
    part = part.strip()
    if " - " in part:
        lo, hi = part.split(" - ", 1)
        part = f">={lo.strip()} <={hi.strip()}"
    part = re.sub(r"(>=|<=|>|<|=|\^|~)\s+", r"\1", part)
    comps = [_comparator(t) for t in part.split()] or [_comparator("*")]
    return lambda v: all(c(v) for c in comps)


def max_satisfying(versions, spec):
    """Наибольшая версия из versions, подходящая под spec; None, если нет/не разобрать."""
    try:
        preds = [_range_predicate(p) for p in spec.split("||")]
    except ValueError:
        return None
    best, best_t = None, None
    for s in versions:
        t = parse_version(s)
        if t is None:
            continue
        if any(p(t) for p in preds) and (best_t is None or t > best_t):
            best, best_t = s, t
    return best
