import unittest
from unittest import TestCase
import doctest
import yaml
from .. import resolver


class TestTagData(TestCase):
  def test_tags(self):
    self.assertEqual(
      resolver.TAGS[resolver.QUOTE_AS_STRINGS]['tag'],
      '!stubbly/quote-as-strings'
    )
    self.assertEqual(
      resolver.TAGS[resolver.SYMBOL]['tag'],
      '!stubbly/symbol'
    )
    self.assertEqual(
      resolver.TAGS[resolver.ESCAPED_DOLLAR]['tag'],
      '!stubbly/escaped-dollar'
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
      "  - $$escaped-dollar\n"
    )
    expected = (
      "- normal_node: 1\n"
      "- !stubbly/symbol '$symbol'\n"
      "- !stubbly/symbol '$code-block':\n"
      "  - another-normal-node\n"
      "  - !stubbly/quote-as-strings '$quote-as-strings': foo\n"
      "  - !stubbly/escaped-dollar '$$escaped-dollar'\n"
    )
    loader = resolver.loader(document)
    self.assertTrue(loader.check_data())
    self.assertEqual(expected, yaml.serialize(loader.get_node()))

def load_tests(loader, tests, ignore):
  tests.addTests(doctest.DocTestSuite(resolver))
  return tests
