import os
import unittest

from depviz.asciitree import render_tree
from depviz.config import parse_config
from depviz.errors import ConfigError, RepositoryError
from depviz.graph import build_graph
from depviz.loadorder import load_order
from depviz.mermaid import to_mermaid
from depviz.semver import max_satisfying
from depviz.testrepo import TestRepository

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


def g(name, root):
    return build_graph(root, TestRepository(os.path.join(EX, name)))


class Tests(unittest.TestCase):
    def test_semver(self):
        v = ["1.0.0", "1.2.3", "1.9.0", "2.0.0", "2.1.0-beta.1", "0.2.5", "0.3.0"]
        self.assertEqual(max_satisfying(v, "^1.0.0"), "1.9.0")
        self.assertEqual(max_satisfying(v, "~1.2.0"), "1.2.3")
        self.assertEqual(max_satisfying(v, "^0.2.0"), "0.2.5")
        self.assertEqual(max_satisfying(v, ">=1.0.0 <2.0.0"), "1.9.0")
        self.assertEqual(max_satisfying(v, "1.x"), "1.9.0")
        self.assertEqual(max_satisfying(v, "1.0.0 || 2.0.0"), "2.0.0")
        self.assertEqual(max_satisfying(v, "*"), "2.0.0")
        self.assertEqual(max_satisfying(v, "1.0.0 - 1.5.0"), "1.2.3")

    def test_diamond_order(self):
        gr = g("simple.txt", "A")
        self.assertEqual(load_order(gr), ["D", "B", "C", "A"])
        self.assertEqual(gr.cycles, [])

    def test_cycle(self):
        gr = g("cycle.txt", "A")
        self.assertEqual(gr.cycles, [["A", "B", "C", "A"]])
        self.assertEqual(load_order(gr), ["D", "C", "B", "A"])
        self.assertIn("-.->", to_mermaid(gr))
        self.assertIn("(цикл)", render_tree(gr))

    def test_self_loop(self):
        gr = g("self.txt", "A")
        self.assertIn(["A", "A"], gr.cycles)

    def test_tree(self):
        t = render_tree(g("big.txt", "A"))
        self.assertIn("├── B", t)
        self.assertIn("(уже показан выше)", t)

    def test_config_errors(self):
        for argv in (["-p", "A", "-t"], ["-p", "a", "-t", "-r", f"{EX}/simple.txt"],
                     ["-p", "A", "-t", "-r", "nope.txt"], ["-p", "Bad Name"],
                     ["-p", "express", "-r", "ftp://x"], ["-p", "express", "-o", "x.jpg"],
                     ["-p", "express", "-o", "/no/such/dir/x.png"], []):
            with self.assertRaises(ConfigError, msg=argv):
                parse_config(argv)

    def test_bad_repo_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("A B C\n")
        with self.assertRaises(RepositoryError):
            TestRepository(f.name)
        os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
