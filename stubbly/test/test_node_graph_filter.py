import unittest
from unittest import TestCase
import doctest
from .. import node_graph_filter

def load_tests(loader, tests, ignore):
  tests.addTests(doctest.DocTestSuite(node_graph_filter))
  return tests
