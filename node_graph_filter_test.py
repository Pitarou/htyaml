#!/usr/bin/env python
import unittest
from unittest import TestCase
import doctest
import yaml
import node_graph_filter

def load_tests(loader, tests, ignore):
  tests.addTests(doctest.DocTestSuite(node_graph_filter))
  return tests

class TestMakeLoader(TestCase):
  "Test that words beginning with '$' and '$quote-as-strings' are tagged"

  def test_make_loader(self):
    document = (
      "normal_node: 1\n"
      "$code:\n"
      "- $nested_code: 2\n"
      "- another_normal_node:\n"
      "  - $quote-as-strings:\n"
      "    - quoted\n"
      "    - content\n"
      "    - $variable\n"
    )
    expected = (
      "normal_node: 1\n"
      "!stubbly '$code':\n"
      "- !stubbly '$nested_code': 2\n"
      "- another_normal_node:\n"
      "  - !stubbly/quote-as-strings '$quote-as-strings':\n"
      "    - quoted\n"
      "    - content\n"
      "    - !stubbly '$variable'\n"
    )
    loader = node_graph_filter.make_loader(document)
    self.assertTrue(loader.check_data())
    self.assertEqual(expected, yaml.serialize(loader.get_node()))

if __name__ == '__main__':
  unittest.main()