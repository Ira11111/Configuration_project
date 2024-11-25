import os
import unittest
from python_mermaid.diagram import Node
from homework2.src.dependencies_vis import (get_dependencies_current, get_all_dependencies,
                                            get_mermaid_str, is_node_in_list, find_node_by_name, make_mermaid_file, get_graph_png)


class TestDependencies(unittest.TestCase):

    def test_get_dependencies_current(self):
        with self.subTest("success"):
            p_name = "react"
            r_dep = "loose-envify"
            res = get_dependencies_current(p_name)
            self.assertTrue(r_dep in res.keys())

        with self.subTest("fail"):
            p_name = "имя"
            r_resp = "Нет данных о пакете имя"
            with self.assertRaises(Exception) as e:
                get_dependencies_current(p_name)
            self.assertEqual(str(e.exception), r_resp)

    def test_get_all_dependencies(self):
        with self.subTest("maximum depth"):
            p_name = "react"
            r_res = {'react': {'loose-envify': '^1.1.0'}, 'loose-envify': {'js-tokens': '^3.0.0 || ^4.0.0'}, 'js-tokens': {}}
            res = {}
            get_all_dependencies(p_name, depth=10, dep_dict=res)
            self.assertEqual(r_res, res)

        with self.subTest("not full depth"):
            p_name = "react"
            res = {}
            get_all_dependencies(p_name, depth=1, dep_dict=res)
            self.assertTrue(len(res) == 1)


class TestGraph(unittest.TestCase):

    def test_is_node_in_list(self):
        nodes = [Node("A"), Node("B")]
        self.assertTrue(is_node_in_list("A", nodes))
        self.assertFalse(is_node_in_list("C", nodes))

    def test_find_node_by_name(self):
        nodes = [Node("A"), Node("B")]
        self.assertEqual(find_node_by_name("A", nodes).content, "A")

    def test_get_mermaid_str(self):
        dependencies = {"a": {"b": "version", "c": "version"}, "c": {"d": "version"}, "b": {}}
        mermaid_str = get_mermaid_str(dependencies)
        self.assertIn("title: Dependencies graph", mermaid_str)
        self.assertIn("a ---> b", mermaid_str)
        self.assertIn("a ---> c", mermaid_str)
        self.assertIn("c ---> d", mermaid_str)

    def test_make_mermaid_file(self):
        path = "test.mmd"
        mermaid_str = """graph\nA ---> B\nA ---> C\nB ---> C"""

        make_mermaid_file(path=path, script_mermaid=mermaid_str)
        self.assertTrue(os.path.exists(path))
        if os.path.exists("test.mmd"):
            os.remove("test.mmd")
