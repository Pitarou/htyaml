#!/usr/bin/env python
import yaml
import markdown2
from .settings import *


class HTYAML(object):
  '''Immutable dict-like object. Child classes should implement render and parse.

    >>> h = HTYAML(foo = 1, bar = 2)
    >>> h
    HTYAML(bar = 2, foo = 1)
    >>> h.foo
    1

Two HTYAML objects are equal if the types and contents are equal:

    >>> HTYAML(foo = 1) == HTYAML(foo = 1)
    True

    >>> HTYAML(foo = 1) == HTYAML(foo = 1, bar = 2)
    False

    >>> class SubClass(HTYAML): pass
    ...
    >>> HTYAML(foo = 1) == SubClass(foo = 1)
    False
'''

  @classmethod
  def _not_implemented(cls, method_name):
    raise TypeError('{class_name}.{method_name}() not implemented'.format(
      class_name = cls.__name__,
      method_name = method_name
    ))

  @classmethod
  def parse(cls, obj):
    '''Parse the object as a list of nodes.'''
    return Nodes.parse(obj)

  @classmethod
  def parse_yaml(cls, yaml_src, **kwargs):
    '''Parse the object returned by yaml.load(yaml_src).'''
    return cls.parse(yaml.load(yaml_src), **kwargs)

  @classmethod
  def fail(cls, yaml_node, message):
    '''Returns a `NotParsed` object to indicate that a parser could not parse this node.

    >>> HTYAML.fail('node', 'reason')
    NotParsed(message = 'HTYAML: reason', yaml_node = 'node')
'''
    full_message = '{class_name}: {message}'.format(
      class_name = cls.__name__,
      message = message
    )
    return NotParsed(yaml_node = yaml_node, message = full_message)


  def render(self, **kwargs):
    self._not_implemented('render')

  def preferred_render_style(self, **kwargs):
    self._not_implemented('preferred_render_style')

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def __setattr__(self, name, value):
    raise TypeError('{class_name} is immutable'.format(
      class_name = self.__class__.__name__
    ))


  def __repr__(self):
    '''To ensure predictable output in unit tests,
the list of constructors is sorted in rendering.

    >>> HTYAML(d = 'd', a = 'a', c = 'c', b = 'b')
    HTYAML(a = 'a', b = 'b', c = 'c', d = 'd')
'''
    class_name = self.__class__.__name__
    item_list = list(self.__dict__.items())
    item_list.sort()
    items = ', '.join('%s = %s' % (name, repr(value)) for name, value in item_list)
    return '{class_name}({items})'.format(
      class_name = class_name,
      items = items
    )

  def __eq__(self, other):
    return type(self) == type(other) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)



class NotParsed(HTYAML):
  _render_template = (
    'Could not parse:\n'
    '{yaml_node}\n'
    '{message}'
  )
  def render(self):
      return self._render_template.format(
        yaml_node = yaml.dump(self.yaml_node, default_flow_style = False),
        message = self.message
      )



class Node(HTYAML):
  r'''Parses and renders text and HTML elements.
`parse` returns an instance of one of the child classes,
which should implement the `render` method.

    >>> Node.parse_yaml('un & escaped').render()
    'un & escaped'

    >>> Node.parse_yaml('hr:').render()
    '<hr>'
'''
  
  @classmethod
  def parse(cls, yaml_node):
    result = Text.parse(yaml_node)
    if isinstance(result, NotParsed):
      result = Element.parse(yaml_node)
      if isinstance(result, NotParsed):
        result = cls.fail(yaml_node, 'not a valid HTML node')
    return result

  @staticmethod
  def _add_prefix(text, kwargs):
    prefix = get_kwarg_with_default(kwargs, 'line_prefix')
    if not prefix:
      return text
    lines = text.splitlines(keepends = True)
    return ''.join(prefix + line for line in lines)

class Text(Node):
  '''Parses and renders text and text-like nodes.
`parse` returns an instance of one of the child classes,
which should implement the `render` method.

    >>> literal = Text.parse('un & escaped')
    >>> type(literal) #doctest: +ELLIPSIS
    <class '...Literal'>
    >>> literal.render()
    'un & escaped'

    >>> escapable = Text.parse(['this is & escaped'])
    >>> type(escapable) #doctest: +ELLIPSIS
    <class '...EscapableText'>
    >>> escapable.render()
    'this is &amp; escaped'
    >>> escapable.render(markdown = True)
    '<p>this is &amp; escaped</p>'
'''
  

  @classmethod
  def parse(cls, yaml_node):
    result = Literal.parse(yaml_node)
    if isinstance(result, NotParsed):
      result = EscapableText.parse(yaml_node)
      if isinstance(result, NotParsed):
        result = cls.fail(yaml_node, 'not a valid text node')
    return result


class Literal(Text):
  '''\
Handles unescaped text, which is represented in yaml by a plain string.

Take care that the yaml parser does not convert your text to something else.
e.g.:

    >>> Literal.parse_yaml('123')
    NotParsed(message = 'Literal: not text', yaml_node = 123)

    >>> Literal.parse_yaml('"123"')
    Literal(literal = '123', yaml_node = '123')
'''

  @classmethod
  def parse(cls, yaml_node):

    if type(yaml_node) is not str:
      return cls.fail(yaml_node, 'not text')

    return cls(literal = yaml_node, yaml_node = yaml_node)

  def render(self, **kwargs):
    return self._add_prefix(self.literal, kwargs)

  def preferred_render_style(self, **kwargs):
    return RENDER_INLINE

class EscapableText(Text):
  r'''Text with conversion or HTML entity escaping. Nulls are also accepted.

    >>> t = EscapableText.parse_yaml('- Jekyll & Hyde')
    >>> t
    EscapableText(text = 'Jekyll & Hyde', yaml_node = ['Jekyll & Hyde'])
    >>> t.render()
    'Jekyll &amp; Hyde'
    >>> t.render(markdown = True)
    '<p>Jekyll &amp; Hyde</p>'

Beware of numbers, booleans and so on:

    >>> EscapableText.parse_yaml('- yes')
    NotParsed(message = 'EscapableText: not singleton list containing text or null', yaml_node = [True])

    >>> EscapableText.parse_yaml('- null').render()
    ''

To avoid these problems, wrap the text in quotes:

    >>> EscapableText.parse_yaml('- "yes"').render()
    'yes'

With `markdown = True` the text is also passed through the Markdown2
renderer. Specify Markdown2 extra features with the `markdown_extras` argument:

    >>> print(EscapableText.parse_yaml("""- |
    ...  Markdown Text
    ...  =============
    ...
    ...  Markdown --- a standard for converting
    ...  human-readable plain text documents
    ...  into HTML.
    ... """).render(markdown = True, markdown_extras = ["smarty-pants"]))
    <h1>Markdown Text</h1>
    <BLANKLINE>
    <p>Markdown &#8212; a standard for converting
    human-readable plain text documents
    into HTML.</p>
'''

  @classmethod
  def parse(cls, yaml_node):
    if type(yaml_node) is not list or len (yaml_node) is not 1:
      return cls.fail(yaml_node, 'not a singleton list')
    text = yaml_node[0]
    if type(text) is not str and text is not None:
      return cls.fail(yaml_node, 'not singleton list containing text or null')
    return cls(text = text, yaml_node = yaml_node)

  def render(self, **kwargs):

    result = self.text

    if result is None:
      return ''

    markdown = get_kwarg_with_default(kwargs, 'markdown')
    if markdown:
      extras = get_kwarg_with_default(kwargs, 'markdown_extras')
      result = markdown2.markdown(result, extras = extras)
      result = result[:-1] # remove the trailing newline
    else:
      result = escape(result, quote = False)

    line_prefix = get_kwarg_with_default(kwargs, 'line_prefix')
    return self._add_prefix(result, kwargs)

  def preferred_render_style(self, **kwargs):
    return RENDER_BLOCK if get_kwarg_with_default(kwargs, 'markdown') else RENDER_INLINE


class Attributes(Node):
  """Renders an attributes dict. Quotes, ampersands and so on are escaped.

    >>> Attributes(attributes = {'value': AttributeValue.parse('"a & b"')}).render()
    ' value="&quot;a &amp; b&quot;"'

Null attribute names are discarded (although the yaml_node retains them):

    >>> Attributes(attributes = {None: None}, yaml_node = {None: None})
    Attributes(attributes = {}, yaml_node = {None: None})

Attributes are rendered in ASCIIbetical order.
Ampersands, quotes, and so on are escaped.

    >>> PotentiallyAmbiguousAttributes.parse_yaml('''
    ... d: d
    ... a: '"a"'
    ... c: c
    ... b: b
    ... ''').render()
    ' a="&quot;a&quot;" b="b" c="c" d="d"'
"""

  def __init__(self, *args, **kwargs):
    if ('attributes' in kwargs):
        attributes = kwargs['attributes']
        if None in attributes:
          kwargs = kwargs.copy()
          attributes = attributes.copy()
          del attributes[None]
          kwargs['attributes'] = attributes
    super(Attributes, self).__init__(*args, **kwargs)
  
  _render_template = ' {name}="{value}"'
  @classmethod
  def _render_item(cls, name, value, **kwargs):
    return cls._render_template.format(
      name = name,
      value = value.render(**kwargs)
    )

  @classmethod
  def _convert_dict_entries_to_attribute_values(cls, d):
    result = {}
    for name, value in d.items():
      converted = AttributeValue.parse(value)
      if isinstance(converted, NotParsed):
        return parsed_value
      result[name] = converted
    return result

  @classmethod
  def empty(cls, yaml_node = None):
    '''Class method to construct an empty attribute list.

If not specified, yaml_node is None.

    >>> Attributes.empty()
    Attributes(attributes = {}, yaml_node = None)

    >>> Attributes.empty(yaml_node = {})
    Attributes(attributes = {}, yaml_node = {})

Constructs instances of the child class when called on child classes:

    >>> class ChildClass(Attributes): pass
    ...
    >>> ChildClass.empty()
    ChildClass(attributes = {}, yaml_node = None)
'''
    return cls(attributes = {}, yaml_node = yaml_node)

  def render(self, **kwargs):
    attributes = list(self.attributes.items())
    attributes.sort()
    return ''.join(self._render_item(name, value, **kwargs) for name, value in attributes)


class AttributeValue(HTYAML):
    '''Handles attribute values. Special handling for nulls, booleans and numbers.
Be carful:

    >>> AttributeValue.parse_yaml('on').render()
    'true'

    >>> AttributeValue.parse(None).render()
    ''

To avoid special handling, force YAML to treat the value as a string
by wrapping it in quotes:

    >>> AttributeValue.parse_yaml('+123').render()
    '123'

    >>> AttributeValue.parse_yaml('"+123"').render()
    '+123'

Quotes, ampersands, and so on are escaped:
    >>> AttributeValue.parse('"').render()
    '&quot;'
'''

    @classmethod
    def parse(cls, yaml_node):
      if yaml_node is not None and type(yaml_node) not in (str, int, bool, float):
        return cls.fail(yaml_node, 'must be text, a number, a bool, or null')
      return cls(value = yaml_node, yaml_node = yaml_node)

    def render(self, **kwargs):
      if self.value is None:
        return ''
      if type(self.value) is bool:
        return 'true' if self.value else 'false'
      if type(self.value) is str:
        return escape(self.value, quote = True)
      return str(self.value)



class PotentiallyAmbiguousAttributes(Attributes):
  """Handles attribute dicts in contexts where other nodes or text objects are not expected.

    >>> a = PotentiallyAmbiguousAttributes.parse_yaml('width: 75%')
    >>> a.attributes
    {'width': AttributeValue(value = '75%', yaml_node = '75%')}
    >>> a.yaml_node
    {'width': '75%'}
    >>> a.render()
    ' width="75%"'

Nulls are treated as empty attribute lists:

    >>> PotentiallyAmbiguousAttributes.parse(None)
    PotentiallyAmbiguousAttributes(attributes = {}, yaml_node = None)
"""
  
  @classmethod
  def parse(cls, yaml_node):
    if yaml_node is None:
      return cls(attributes = {}, yaml_node = None)
    if type(yaml_node) is not dict:
      return cls.fail(yaml_node, 'not a dict or null')
    attributes = cls._convert_dict_entries_to_attribute_values(yaml_node)
    return cls(
      attributes = attributes,
      yaml_node = yaml_node
    )

class UnambiguousAttributes(Attributes):
  """Handles attribute dicts in contexts where other nodes might be expected.
To avoid confusion, the attribute list must be multiple, or wrapped in a list.

  >>> UnambiguousAttributes.parse_yaml('width: 75%') #doctest: +NORMALIZE_WHITESPACE
  NotParsed(message = 'UnambiguousAttributes:
      to distinguish an attribute dict of length 1 from an HTML element
      wrap it in a list',
    yaml_node = {'width': '75%'})
"""

  @classmethod
  def parse(cls, yaml_node):
    if yaml_node in [None, {}, [], [None], [{}]]:
      return cls.empty(yaml_node = yaml_node)

    if type(yaml_node) is dict and len(yaml_node) is 1:
      return cls.fail(
        yaml_node,
        ('to distinguish an attribute dict of length 1 ' +
          'from an HTML element wrap it in a list')
      )

    if type(yaml_node) is not list:
      node = yaml_node
    elif len(yaml_node) is not 1:
      return cls.fail(
        yaml_node,
        'a list wrapping an attribute dict must be of length 1'
      )
    else:
      node = yaml_node[0]

    if type(node) is not dict:
      return cls.fail(
        yaml_node,
        'not a dict, a null, or a list containing a dict or null'
      )

    attributes = cls._convert_dict_entries_to_attribute_values(node)
    return cls(attributes = attributes, yaml_node = yaml_node)


class Element(Node):
  r'''Parses and renders text and text-like nodes.
`parse` returns an instance of one of the child classes,
which should implement the `render` method.

    >>> Element.parse_yaml('hr:').render()
    '<hr>'

An element that requires a closing tag is marked
by the fact that it contains text or a list.
A self-closing element can only contain a dict or null.

    >>> Element.parse_yaml('div: text').render()
    '<div>text</div>'

    >>> Element.parse_yaml('div:\n - - markdown text').render(markdown = True)
    '<div>\n  <p>markdown text</p>\n</div>'

    >>> Element.parse({'div': []}).render()
    '<div></div>'

    >>> Element.parse_yaml('hr: {width: 75%}').render()
    '<hr width="75%">'
'''
  @classmethod
  def parse(cls, yaml_node):
    element = EmptyElement.parse(yaml_node)
    if isinstance(element, NotParsed):
      element = ElementWithContent.parse(yaml_node)
      if isinstance(element, NotParsed):
        return cls.fail(
          yaml_node,
          'not a valid element'
        )
    return element

class EmptyElement(Element):
  """Denoted by a singleton dict containing an attribute dict or null.

    >>> print(EmptyElement.parse_yaml('''
    ... link:
    ...   rel: stylesheet
    ...   type: text/css
    ...   href: styles.css
    ... ''').render())
    <link href="styles.css" rel="stylesheet" type="text/css">

    >>> print(EmptyElement.parse_yaml('hr:').render())
    <hr>
"""

  @classmethod
  def parse(cls, yaml_node):
    if type(yaml_node) is not dict or len(yaml_node) is not 1:
      return cls.fail(yaml_node, 'not a dict containing 1 entry')
    tag, attributes_dict = yaml_node.copy().popitem()
    attributes = PotentiallyAmbiguousAttributes.parse(attributes_dict)
    if isinstance(attributes, NotParsed):
      return attributes
    return cls(tag = tag, attributes = attributes, yaml_node = yaml_node)

  _render_template = '{line_prefix}<{tag}{attributes}>'
  def render(self, **kwargs):
    return self._render_template.format(
      tag = self.tag,
      attributes = self.attributes.render(**kwargs),
      line_prefix = get_kwarg_with_default(kwargs, 'line_prefix')
    )

  def preferred_render_style(self, **kwargs):
    style = get_tag_render_style(kwargs, self.tag)
    if style == RENDER_ACCORDING_TO_CHILDREN:
      # This shouldn't really happen, but let's accommodate it
      # as best we can.
      return RENDER_INLINE
    else:
     return style


class ElementWithContent(Element):
  r"""Denoted by a singleton dict containing text;
or a list containing an attribute dict and child nodes.

    >>> e = ElementWithContent.parse_yaml('''
    ...   div:
    ...     - class: jumbotron
    ...       ?
    ...     - - content
    ... ''')
    >>> print(e.render(markdown = True))
    <div class="jumbotron">
      <p>content</p>
    </div>
"""
  
  @classmethod
  def parse(cls, yaml_node):

    if type(yaml_node) is not dict or len(yaml_node) is not 1:
      return cls.fail(yaml_node, 'not a dict containing 1 entry')

    tag, content = yaml_node.copy().popitem()

    # Handle empty content list
    if content in ([], [None]):
      return cls(
        tag = tag,
        attributes = Attributes.empty(),
        nodes = Nodes.empty(),
        yaml_node = yaml_node
    )

    # Attempt to pull out attributes list
    if type(content) is list:
      attributes = UnambiguousAttributes.parse(content[0])
      if isinstance(attributes, NotParsed):
        attributes = Attributes.empty()
      else:
        content = content[1:]
    else:
      attributes = Attributes.empty()

    parsed_content = Nodes.parse(content)

    if isinstance(parsed_content, NotParsed):
      return parsed_content

    return cls(
      tag = tag,
      attributes = attributes,
      nodes = parsed_content,
      yaml_node = yaml_node
    )

  def preferred_render_style(self, **kwargs):
    style = get_tag_render_style(kwargs, self.tag)
    if style != RENDER_ACCORDING_TO_CHILDREN:
      return style
    return self.nodes.preferred_render_style()

  _render_template_inline = '{line_prefix}<{tag}{attributes}>{content}</{tag}>'
  _render_template_block = (
    '{line_prefix}<{tag}{attributes}>\n'
    '{content}\n'
    '{line_prefix}</{tag}>'
  )
  def render(self, **kwargs):

    line_prefix = get_kwarg_with_default(kwargs, 'line_prefix')
    tag = self.tag
    attributes = self.attributes.render(**kwargs)
    kwargs['line_prefix'] = line_prefix + '  '
    nodes = self.nodes
    content = nodes.render(**kwargs)
    if nodes.preferred_render_style(**kwargs) == RENDER_BLOCK:
      template = self._render_template_block
    else:
      template = self._render_template_inline
    return template.format(
      line_prefix = line_prefix,
      tag = tag,
      attributes = attributes,
      content = content
    )


class Nodes(HTYAML):
  r'''Either a single Node, or a list of any number of Nodes.
  Supports len and list indexing.

    >>> Nodes.parse_yaml('hr:').render()
    '<hr>'
    >>> n = Nodes.parse_yaml("""
    ... - li: one
    ... - li: two
    ... """)
    >>> print(n.render())
    <li>one</li>
    <li>two</li>
    >>> len(n)
    2
    >>> print(n[0].render())
    <li>one</li>
'''

  @classmethod
  def parse(cls, yaml_node):
    if type(yaml_node) is not list:
      parsed_node = Node.parse(yaml_node)
      if isinstance(parsed_node, NotParsed):
        return parsed_node
      else:
        return cls(nodes = [parsed_node], yaml_node = yaml_node)

    parsed_nodes = []
    for node in yaml_node:
      parsed_node = Node.parse(node)
      if isinstance(parsed_node, NotParsed):
        return parsed_node
      parsed_nodes.append(parsed_node)
    return cls(nodes = parsed_nodes, yaml_node = yaml_node)

  def preferred_render_style(self, **kwargs):
    if len(self) == 0:
      return RENDER_INLINE
    for node in self:
      if node.preferred_render_style(**kwargs) == RENDER_BLOCK:
        return RENDER_BLOCK
    return RENDER_INLINE


  @classmethod
  def empty(cls):
    return cls(nodes = [], yaml_node = None)

  def render(self, **kwargs):

    if len(self) is 0:
      return ''

    if self.preferred_render_style(**kwargs) == RENDER_BLOCK:
      return '\n'.join(node.render(**kwargs) for node in self)

    kwargs['line_prefix'] = ''
    return ' '.join(node.render(**kwargs) for node in self)


  def __len__(self):
    return len(self.nodes)

  def __getitem__(self, index):
    return self.nodes[index]

  def __iter__(self):
    return self.nodes.__iter__()

if __name__ == '__main__':
  from sys import argv
  if len(argv) is 1:
    from doctest import testmod
    testmod()
  else:
    print(HTYAML.parse_yaml(open(argv[1])).render(markdown = True))
