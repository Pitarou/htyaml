from .stubbly import SingletonStubblyObject
class QuoteAsStrings(SingletonStubblyObject):

  resolver_regexp = r'^\$quote-as-strings$'
  resolver_first = '$'

  def __repr__(self):
    return self.__class__.__name__ + '()'

  @classmethod
  def from_yaml(cls, loader, node):
    return cls()

  @classmethod
  def to_yaml(cls, dumper, data):
    return dumper.represent_scalar(
      dumper.DEFAULT_SCALAR_TAG,
      '$quote-as-strings'
    )