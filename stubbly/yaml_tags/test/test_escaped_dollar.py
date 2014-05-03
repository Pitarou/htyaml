import unittest
from unittest import TestCase
from io import StringIO
import yaml
from .. import resolver, escaped_dollar

class TestEscapedDollar(TestCase):
  yaml_src = (
    '- $$escaped\n'
    '- not $$escaped\n'
  )
  expected_object = [
    escaped_dollar.EscapedDollar('$$escaped'),
    'not $$escaped'

  ]
  expected_representation = (
    "[$$escaped, not $$escaped]\n"
  )

  def setUp(self):
    self.loader = resolver.loader(self.yaml_src)
    tag = resolver.TAGS[resolver.ESCAPED_DOLLAR]['tag']
    self.loader.add_constructor(tag, escaped_dollar.constructor)

  def test_load_object(self):
    self.assertTrue(self.loader.check_data())
    data = self.loader.get_data()
    self.assertEqual(data, self.expected_object)
    self.assertEqual(type(data[0]), escaped_dollar.EscapedDollar)

  def test_dump(self):
    data = self.loader.get_data()
    stream = StringIO()
    dumper = yaml.Dumper(stream)
    dumper.add_representer(
      escaped_dollar.EscapedDollar,
      escaped_dollar.representer
    )
    dumper.open()
    dumper.represent(data)
    self.assertEqual(
      self.expected_representation,
      stream.getvalue()
    ) 

  def test_acts_like_string(self):
    self.assertEqual('$', escaped_dollar.EscapedDollar('$$'))
    self.assertEqual(escaped_dollar.EscapedDollar('$$'), '$')
