import re
import yaml


class StubblyObjectMetaclass(yaml.YAMLObjectMetaclass):
  tag_prefix = '!stubbly/'

  def __init__(cls, name, bases, kwds):
    super(cls.__class__, cls).__init__(name, bases, kwds)
    
    first_letter = name[0].lower()
    rest = ['-'+c.lower() if c.isupper() else c for c in name[1:]]
    yaml_tag = cls.tag_prefix + first_letter + ''.join(rest)
    cls.yaml_tag = yaml_tag

    cls.yaml_loader.add_constructor(yaml_tag, cls.from_yaml)
    cls.yaml_dumper.add_representer(yaml_tag, cls.to_yaml)

    regexp = kwds.get('resolver_regexp')
    first = kwds.get('resolver_first')
    if regexp is not None:
      compiled = re.compile(regexp)
      yaml.add_implicit_resolver(
        yaml_tag,
        compiled,
        Loader = cls.yaml_loader,
        Dumper = cls.yaml_dumper,
        first = first 
      )


StubblyObject = StubblyObjectMetaclass(
  'StubblyObject', (yaml.YAMLObject,), {}
)

StubblyObject.__doc__ = '''\n
Extension of YAMLObject that automatically infers the yaml_tag
field from the class' name, and automatically registers
a resolver from the supplied `resolver_regexp` and
`resolver_first` fields.
'''

class SingletonStubblyObject(StubblyObject):
  '''Singleton version of StubblyObject.'''
  _instances = {}
  def __new__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(
        SingletonStubblyObject, cls
      ).__new__(cls, *args, **kwargs)
    return cls._instances[cls]
