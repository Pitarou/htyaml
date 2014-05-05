from .stubbly import StubblyObject

class Symbol(StubblyObject, str):

  # Any string starting with '$', but not with '$$',
  # except '$quote-as-strings'
  resolver_regexp = r'^\$(?!\$|quote-as-strings$)'
  resolver_first = '$'
  
  def __new__(cls, string):
    if string.startswith('$'):
      string = string [1:]
    return str.__new__(cls, string)

  def __repr__(self):
    return (
      self.__class__.__name__ + '(' + repr('$' + self) + ')'
    )
    

  @classmethod
  def from_yaml(cls, loader, node):
    return cls(loader.construct_scalar(node))

  @classmethod
  def to_yaml(cls, dumper, data):
    return dumper.represent_scalar(
      dumper.DEFAULT_SCALAR_TAG,
      '$' + data
    )
