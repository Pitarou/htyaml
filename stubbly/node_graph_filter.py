#!/usr/bin/env python
import re
import yaml
from yaml import SequenceNode, MappingNode, ScalarNode
from .yaml_tags import resolver

_string_tag = yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG
_quote_as_strings_tag = resolver.TAGS[
  resolver.QUOTE_AS_STRINGS
]['tag']
_symbol_tag = resolver.TAGS[
  resolver.SYMBOL
]['tag']

def scalars_to_strings(node, everything = False):
  r'''Turn scalars into strings, except for dict keys and !stubbly content.
Also turn !stubbly/quote-as-strings content into strings.

    >>> document = """ 
    ...   number: 5
    ...   boolean: on
    ...   null:
    ...   unquoted: hello
    ...   quoted: 'hello'
    ...   sequence:
    ...     - 1 # SHOULD be converted to a string
    ...     - 2: [3, 4] # 2 shoud NOT be converted to a string
    ...   $code:
    ...   - 4 # should NOT be converted to a string
    ...   - $quote-as-strings:
    ...     - 5: 6 # should ALL be converted to a string
    ...     - $code: 6 # SHOULD be converted to strings
    ...   ?
    ... """
    >>> loader = resolver.loader(document)
    >>> loader.check_data()
    True
    >>> node = loader.get_node()
    >>> stringified = scalars_to_strings(node)
    >>> print(yaml.serialize(stringified).strip())
    number: '5'
    boolean: 'on'
    null: ''
    unquoted: hello
    quoted: 'hello'
    sequence:
    - '1'
    - 2:
      - '3'
      - '4'
    !stubbly/symbol '$code':
    - 4
    - !stubbly/quote-as-strings '$quote-as-strings':
      - '5': '6'
      - $code: '6'
    ?
    : ''
  '''
  tag = node.tag
  value = node.value
  if type(node) is SequenceNode:
    return SequenceNode(
      tag = tag,
      value = [scalars_to_strings(item, everything) for item in value]
    )

  if type(node) is ScalarNode:
    if tag == _string_tag:
      return node
    return ScalarNode(
      tag = _string_tag,
      value = value
    )

  return MappingNode(
    tag = tag,
    value = [
      mapping_item_to_strings(
        item,
        everything
      ) for item in value
    ]
  )

  


def mapping_item_to_strings(item, everything = False):
  key, value = item

  if everything:
    key = scalars_to_strings(key, everything = True)
    value = scalars_to_strings(value, everything = True)
    return (key, value)

  if key.tag.startswith(resolver.TAG_PREFIX):
    return check_code_for_quote_as_strings(item)
  else:
    return (key, scalars_to_strings(value))


def check_code_for_quote_as_strings(item):
  key, value = item
  if key.tag is _quote_as_strings_tag:
    return (
      key,
      scalars_to_strings(value, everything = True)
    )
  return (
    key,
    search_for_quote_as_strings(value)
  )


def search_for_quote_as_strings(node):

  if type(node) is ScalarNode:
    return node

  tag = node.tag 
  value = node.value

  if type(node) is SequenceNode:
    return SequenceNode(
        tag = tag,
        value = [search_for_quote_as_strings(item) for item in value]
    )

  return MappingNode(
    tag = tag,
    value = [check_code_for_quote_as_strings(item) for item in value]
  )


def load_as_strings(stream):
  '''Like yaml.load (kinda ... I'm still getting to grips with the API),
but with a filter that converts all scalars to strings.

    >>> load_as_strings('[null, 1]')
    ['null', '1']
'''
  loader = yaml.Loader(stream)
  loader.check_node()
  node = loader.get_node()
  node = scalars_to_strings(node)
  if type(node) is SequenceNode:
    return loader.construct_sequence(node)
  if type(node) is MappingNode:
    return loader.construct_mapping(node)
  return loader.construct_scalar(node)


import yaml

if __name__ == '__main__':
  from doctest import testmod
  testmod()