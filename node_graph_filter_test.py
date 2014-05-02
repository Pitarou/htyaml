#!/usr/bin/env python
import unittest
from unittest import TestCase
import doctest
import yaml
import node_graph_filter
import stubbly_resolver

def load_tests(loader, tests, ignore):
  tests.addTests(doctest.DocTestSuite(node_graph_filter))
  return tests

if __name__ == '__main__':
  unittest.main()