#!/usr/bin/env python
import yaml
import re

STUBBLY = 'stubbly'
QUOTE_AS_STRINGS = 'quote-as-strings'
SYMBOL = 'symbol'
TAG_PREFIX = '!' + STUBBLY + '/'

TAGS = {
  SYMBOL: {
    'tag': TAG_PREFIX + SYMBOL,
    # string starting with '$', but not '$$'
    'regexp': re.compile(r'^\$($|[^$])'),
  },
  QUOTE_AS_STRINGS: {
    'tag': TAG_PREFIX + QUOTE_AS_STRINGS,
    # the exact string '$quote-as-string'
    'regexp': re.compile(r'^\$'+QUOTE_AS_STRINGS+'$'),
  },
}

TAG_RESOLVER_SEQUENCE = [QUOTE_AS_STRINGS, SYMBOL]

def loader(stream):
  'Instantiate a yaml.Loader with implicit resolvers for the stubbly tags.'
  loader = yaml.Loader(stream)
  for tag_type in TAG_RESOLVER_SEQUENCE:
    tag_data = TAGS[tag_type]
    tag, regexp = tag_data['tag'], tag_data['regexp']
    loader.add_implicit_resolver(tag, regexp, first = None)
  return loader

