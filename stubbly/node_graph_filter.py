import yaml
from yaml import SequenceNode, MappingNode, ScalarNode
from yaml.resolver import BaseResolver
from .yaml_tags import *

[BASE, SYMBOL, QUOTE_AS_STRINGS] = range(3)
STUBBLY_TAG_PREFIX = Symbol.tag_prefix
STRING_TAG = BaseResolver.DEFAULT_SCALAR_TAG

def scalars_to_strings(node, state = BASE):
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
    >>> loader = yaml.Loader(document)
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
    $code:
    - 4
    - $quote-as-strings:
      - '5': '6'
      - '$code': '6'
    ?
    : ''
  '''
  tag = node.tag
  value = node.value

  if type(node) is SequenceNode:
    return SequenceNode(
      tag = tag,
      value = [scalars_to_strings(item, state) for item in value]
    )

  if type(node) is MappingNode:
    return MappingNode(
      tag = tag,
      value = [mapping_item_to_strings(item, state) for item in value]
    )

  if (tag == STRING_TAG or
      state is SYMBOL or
      (state is BASE and tag.startswith(STUBBLY_TAG_PREFIX))):
    return node

  return ScalarNode(
    tag = STRING_TAG,
    value = value
  )

def mapping_item_to_strings(item, state = BASE):

  key, value = item
  tag = key.tag
  if state is QUOTE_AS_STRINGS and tag != STRING_TAG:
    key_ = ScalarNode(tag = STRING_TAG, value = key.value)
  else:
    key_ = key
  if state is QUOTE_AS_STRINGS or tag == QuoteAsStrings.yaml_tag:
    next_state = QUOTE_AS_STRINGS
  elif state is SYMBOL or tag == Symbol.yaml_tag:
    next_state = SYMBOL
  else:
    next_state = BASE
  return (key_, scalars_to_strings(value, state = next_state))