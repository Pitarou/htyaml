#!/usr/bin/env python
import unittest
from unittest import TestCase
import doctest
import yaml
import stubbly_resolver


class TestTagData(TestCase):
  def test_tags(self):
    self.assertEqual(
      stubbly_resolver.TAGS[stubbly_resolver.QUOTE_AS_STRINGS]['tag'],
      '!stubbly/quote-as-strings'
    )
    self.assertEqual(
      stubbly_resolver.TAGS[stubbly_resolver.SYMBOL]['tag'],
      '!stubbly/symbol'
    )

class TestMakeLoader(TestCase):
  "Test that words beginning with '$' and '$quote-as-strings' are tagged"

  def test_make_loader(self):
    document = (
      "- normal_node: 1\n"
      "- $symbol\n"
      "- $code-block:\n"
      "  - another-normal-node\n"
      "  - $quote-as-strings: foo\n"
    )
    expected = (
      "- normal_node: 1\n"
      "- !stubbly/symbol '$symbol'\n"
      "- !stubbly/symbol '$code-block':\n"
      "  - another-normal-node\n"
      "  - !stubbly/quote-as-strings '$quote-as-strings': foo\n"
    )
    loader = stubbly_resolver.loader(document)
    self.assertTrue(loader.check_data())
    self.assertEqual(expected, yaml.serialize(loader.get_node()))

def load_tests(loader, tests, ignore):
  tests.addTests(doctest.DocTestSuite(stubbly_resolver))
  return tests

if __name__ == '__main__':
  unittest.main()