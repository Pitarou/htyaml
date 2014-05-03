#!/usr/bin/env python
import doctest
import yaml
from . import resolver

class EscapedDollar(str):
  def __new__(cls, string):
    if string.startswith('$$'):
      string = string[1:]
    return str.__new__(cls, string)

  def __repr__(self):
    return self

def constructor(loader, node):
  return EscapedDollar(loader.construct_scalar(node))

def representer(dumper, data):
  return dumper.represent_scalar(
    resolver.TAGS[resolver.ESCAPED_DOLLAR]['tag'],
    '$'+data
  )