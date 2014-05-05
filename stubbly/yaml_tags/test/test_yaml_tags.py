import unittest
from unittest import TestCase
import yaml
from .. import *

class TestSymbol(TestCase):

  yaml_src = (
    '- $lonely symbol\n'
    '- $mapping:\n'
    '   - one\n'
    '   - $two\n'
    '- $$not a symbol\n'
  )

  expected_object = [
    Symbol('$lonely symbol'),
    {Symbol('$mapping'): ['one', Symbol('$two')]},
    EscapedDollar('$$not a symbol')
  ]

  def test_yaml_tag(self):
    self.assertEqual(
      Symbol.yaml_tag,
      '!stubbly/symbol'
    )

  def test_repr(self):
    self.assertEqual(
      repr(Symbol('$foo')),
      "Symbol('$foo')"
    )

  def test_resolver(self):
    composed = yaml.compose(self.yaml_src)
    self.assertEqual(
      composed.value[0].tag,
      Symbol.yaml_tag
    )
    self.assertEqual(
      composed.value[1].value[0][0].tag,
      Symbol.yaml_tag
    )
    self.assertEqual(
      composed.value[1].value[0][1].value[1].tag,
      Symbol.yaml_tag
    )
    self.assertNotEqual(
      composed.value[2].tag,
      Symbol.yaml_tag
    )
    self.assertNotEqual(
      composed.value[1].value[0][1].value[0].tag,
      Symbol.yaml_tag
    )


  def test_load(self):
    self.assertEqual(
      self.expected_object,
      yaml.load(self.yaml_src)
    )

  def test_acts_like_string(self):
    self.assertEqual('foo', Symbol('$foo'))
    self.assertEqual(Symbol('$foo'), 'foo')

class TestEscapedDollar(TestCase):

  yaml_src = (
    '- $$escaped\n'
    '- $not escaped\n'
    '- not $$escaped\n'
  )

  expected_object = [
    EscapedDollar('$$escaped'),
    Symbol('$not escaped'),
    'not $$escaped',
  ]

  expected_representation = (
    "[$$escaped, $not escaped, not $$escaped]\n"
  )
  
  def test_yaml_tag(self):
    self.assertEqual(
      EscapedDollar.yaml_tag,
      '!stubbly/escaped-dollar'
    )

  def test_repr(self):
    self.assertEqual(
      repr(EscapedDollar('$$foo')),
      "EscapedDollar('$$foo')"
    )

  def test_resolver(self):
    composed = yaml.compose(self.yaml_src)
    self.assertEqual(
      composed.value[0].tag,
      EscapedDollar.yaml_tag
    ) 
    self.assertNotEqual(
      composed.tag,
      EscapedDollar.yaml_tag)
    self.assertNotEqual(
      composed.value[1].tag,
      EscapedDollar.yaml_tag
    )

  def test_load(self):
    self.assertEqual(
      yaml.load(self.yaml_src),
      self.expected_object
    )

  def test_acts_like_string(self):
    self.assertEqual('$', EscapedDollar('$$'))
    self.assertEqual(EscapedDollar('$$'), '$')

class TestQuoteAsStrings(TestCase):

  yaml_src = (
    '- $quote-as-strings\n'
    '- $dont-quote-as-strings\n'
  )

  expected_object = [
    QuoteAsStrings(),
    Symbol('$dont-quote-as-strings')
  ]

  def test_yaml_tag(self):
    self.assertEqual(
      QuoteAsStrings.yaml_tag,
      '!stubbly/quote-as-strings'
    )

  def test_repr(self):
    self.assertEqual(
      repr(QuoteAsStrings()),
      "QuoteAsStrings()"
    )

  def test_resolver(self):
    composed = yaml.compose(self.yaml_src)
    self.assertEqual(
      composed.value[0].tag,
      QuoteAsStrings.yaml_tag
    )
    self.assertNotEqual(
      composed.value[1].tag,
      QuoteAsStrings.yaml_tag
    )


  def test_load(self):
    self.assertEqual(
      self.expected_object,
      yaml.load(self.yaml_src)
    )

