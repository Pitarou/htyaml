from unittest import TestCase
from ..yaml_tags import *
from ..loader import load

class TestLoad(TestCase):


  def test_ordinary_yaml_object(self):
    yaml_src = '[1, two]'
    obj = load(yaml_src)
    self.assertEqual(['1', 'two'], obj)

  def test_escaped_dollars(self):
    yaml_src = '''
    - 123
    - $$escaped
    - $quote-as-strings
    - $code:
      - $$escaped: 1
      - 2
      - $quote-as-strings:
         - $not-code
         - 3
         - $$not-escaped
    '''
    obj = load(yaml_src)
    self.assertEqual(
      obj,
      [
        '123',
        EscapedDollar('$$escaped'),
        QuoteAsStrings(),
        {
          Symbol('$code'): [
            {EscapedDollar('$$escaped'): 1},
            2,
            {
              QuoteAsStrings(): [
               '$not-code',
               '3',
               '$$not-escaped'
              ]
            }
          ]
        }
      ]
    )