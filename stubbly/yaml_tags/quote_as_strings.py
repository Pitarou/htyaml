from .stubbly import StubblyObject

class QuoteAsStrings(StubblyObject, str):

  resolver_regexp = r'^\$quote-as-strings$'
  resolver_first = '$'

  def __repr__(self):
    return self.__class__.__name__ + '(' + repr(str(self)) + ')'

  @classmethod
  def from_yaml(cls, loader, node):
    return cls(loader.construct_scalar(node))

  @classmethod
  def to_yaml(cls, dumper, data):
    return dumper.represent_scalar(
      dumper.DEFAULT_SCALAR_TAG,
      data
    )