from unittest import TestCase
import doctest
from .. import htyaml
from ..htyaml import HTYAML, NotParsed, Literal, EmptyElement,\
  ElementWithContent, AttributeValue, UnambiguousAttributes,\
  PotentiallyAmbiguousAttributes, Attributes, \
  Text, EscapableText, Element, Node, Nodes

from ..settings import RENDER_INLINE, RENDER_BLOCK,\
  RENDER_ACCORDING_TO_CHILDREN


class ParserRendererTest(TestCase):

  def check_rendering(self, cls, yaml_src, expected, **kwargs):
    actual = cls.parse_yaml(yaml_src).render(**kwargs)
    self.assertEqual(expected, actual)


class TestHTYAML(ParserRendererTest):

  def test_render_not_implemented(self):
    with self.assertRaises(TypeError) as context_manager:
      HTYAML().render()
    args = context_manager.exception.args
    self.assertEqual(args, ('HTYAML.render() not implemented',))

  def test_preferred_render_style_not_implemented(self):
    with self.assertRaises(TypeError) as context_manager:
      HTYAML().preferred_render_style()
    args = context_manager.exception.args
    self.assertEqual(args, ('HTYAML.preferred_render_style() not implemented',))

  def test_parse_render(self):
    self.check_rendering(
      HTYAML,
      'foo & bar',
      'foo & bar'
    )
class TestNotParsed(TestCase):
  def test_render(self):
    self.assertEqual(
      NotParsed(
        yaml_node = 'foo',
        message = 'bad node'
      ).render(),
      'Could not parse:\nfoo\n...\n\nbad node'
    )

class TestLiteral(TestCase):

  def test_normal_text(self):
    self.assertEqual(
      Literal.parse_yaml('literal').render(),
      'literal'
    )

  def test_not_str(self):
    self.assertEqual(
      Literal.parse_yaml('123'),
      NotParsed(message = 'Literal: not text', yaml_node = 123)
    )

  def test_preferred_render_style(self):
    self.assertEqual(Literal.parse('').preferred_render_style(), RENDER_INLINE)



class TestAttributeValue(ParserRendererTest):

  def test_bad_value(self):
    expected = NotParsed(
      message = 'AttributeValue: must be text, a number, a bool, or null',
      yaml_node = []
    )
    actual = AttributeValue.parse([])
    self.assertEqual(expected, actual)

  def test_text(self):
    self.check_rendering(AttributeValue, 'foo', 'foo')

  def test_int(self):
    self.check_rendering(AttributeValue, '+123', '123')

  def test_float(self):
    self.check_rendering(AttributeValue, '1.00000', '1.0')

  def test_true(self):
    self.check_rendering(AttributeValue, 'on', 'true')

  def test_false(self):
    self.check_rendering(AttributeValue, 'no', 'false')

  def test_null(self):
    self.check_rendering(AttributeValue, 'null', '')

  def test_escaping(self):
    self.check_rendering(AttributeValue, """'"&"'""", '&quot;&amp;&quot;')


class TestAttributes(ParserRendererTest):

  def test_empty_node_not_specified(self):
    self.assertEqual(
      Attributes.empty(),
      Attributes(attributes = {}, yaml_node = None)
    )

  def test_empty_node_specified(self):
    self.assertEqual(
      Attributes.empty([]),
      Attributes(attributes = {}, yaml_node = []
    )
  )

  def test_render_empty(self):
    self.assertEqual(
      Attributes.empty().render(), ''
    )

  def test_render_1_attribute(self):
    a = Attributes(
      attributes = {
        'a': AttributeValue(value = 1, yaml_node = 1)
      },
      yaml_node = {'a': 1}
    )
    self.assertEqual(a.render(), ' a="1"')

  def test_render_3_attributes(self):
    a = Attributes(
      attributes = {
        'b': AttributeValue(value = 2, yaml_node = 2),
        'a': AttributeValue(value = 1, yaml_node = 1),
        'c': AttributeValue(value = 3, yaml_node = 3),
      },
      yaml_node = {'b': 2, 'a': 1, 'c': 3}
    )
    self.assertEqual(a.render(), ' a="1" b="2" c="3"')

  def test_discard_null_attributes(self):
    value = AttributeValue(value = 1, yaml_node = 1)
    yaml_node = {'a': 1, None: None}
    actual = Attributes(
      attributes = {
        'a': value,
        None: AttributeValue(value = None, yaml_node = None),
      },
      yaml_node = yaml_node
    )
    expected = Attributes(
      attributes = {
        'a': value,
      },
      yaml_node = yaml_node
    ) 
    self.assertEqual(expected, actual)


class TestPotentiallyAmbiguousAttributes(ParserRendererTest):

  def test_bad_attributes_object(self):
    yaml_src = 'hi there'
    expected = NotParsed(
      message = 'PotentiallyAmbiguousAttributes: not a dict or null',
      yaml_node = 'hi there'
    )
    actual = PotentiallyAmbiguousAttributes.parse_yaml(yaml_src)
    self.assertEqual(expected, actual)

  def test_bat_attributes_list(self):
    expected = NotParsed(
      message = 'PotentiallyAmbiguousAttributes: not a dict or null',
      yaml_node = []
    )
    actual = PotentiallyAmbiguousAttributes.parse([])
    self.assertEqual(expected, actual)

  def test_multiple_attributes(self):
    yaml_src = '''
      rel: stylesheet
      type: text/css
      src: styles.css
    '''
    expected = ' rel="stylesheet" src="styles.css" type="text/css"'
    self.check_rendering(PotentiallyAmbiguousAttributes, yaml_src, expected)

  def test_none(self):
    self.assertEqual(
      PotentiallyAmbiguousAttributes.parse(None),
      PotentiallyAmbiguousAttributes(
        attributes = {},
        yaml_node = None
      )
    )

  def test_empty_dict(self):
    self.assertEqual(
      PotentiallyAmbiguousAttributes.parse({}),
      PotentiallyAmbiguousAttributes(attributes = {}, yaml_node = {})
    )

  def test_singleton_dict(self):
    self.assertEqual(
      PotentiallyAmbiguousAttributes.parse({'a': 1}),
      PotentiallyAmbiguousAttributes(
        attributes = {'a': AttributeValue(value = 1, yaml_node = 1)},
        yaml_node = {'a': 1}
      )
    )


class TestUnambiguousAttributes(ParserRendererTest):

  def test_bad_attributes_list_too_long(self):
    yaml_src = '''
      - a: 1
      - b: 2
    '''
    expected = NotParsed(
      message = (
        'UnambiguousAttributes: a list wrapping an attribute dict '
        'must be of length 1'
      ),
      yaml_node = [{'a': 1}, {'b': 2}]
    )
    actual = UnambiguousAttributes.parse_yaml(yaml_src)
    self.assertEqual(expected, actual)

  def test_bad_attributes_dict_length_1(self):
    yaml_node = {'a': 1}
    expected = NotParsed(
      message = (
        'UnambiguousAttributes: to distinguish an attribute dict '
        'of length 1 from an HTML element wrap it in a list'
      ),
      yaml_node = yaml_node
    )
    actual = UnambiguousAttributes.parse(yaml_node)
    self.assertEqual(expected, actual)

  def test_bad_attributes_wrong_type(self):
    yaml_node = 'foo'
    expected = NotParsed(
      message = (
        'UnambiguousAttributes: not a dict, a null, '
        'or a list containing a dict or null'
      ),
      yaml_node = yaml_node
    )
    actual = UnambiguousAttributes.parse(yaml_node)
    self.assertEqual(expected, actual)

  def test_empty_attributes_list(self):
    expected = UnambiguousAttributes(attributes = {}, yaml_node = [])
    actual = UnambiguousAttributes.parse_yaml('[]')
    self.assertEqual(expected, actual)

  def test_null_attributes_list(self):
    expected = UnambiguousAttributes(attributes = {}, yaml_node = [None])
    actual = UnambiguousAttributes.parse_yaml('- ')
    self.assertEqual(expected, actual)

  def test_wrapped_singleton_attributes_list(self):
    yaml_node = [{'a': 1}]
    value = AttributeValue(value = 1, yaml_node = 1)
    expected = UnambiguousAttributes(
      attributes = {'a': value},
      yaml_node = yaml_node
    )
    actual = UnambiguousAttributes.parse(yaml_node)
    self.assertEqual(expected, actual)

  def test_unwrapped_multiple_attributes(self):
    yaml_node = {'a': 1, 'b': 2}
    expected_attributes = {
      'a': AttributeValue(value = 1, yaml_node = 1),
      'b': AttributeValue(value = 2, yaml_node = 2)
    }
    expected = UnambiguousAttributes(
      attributes = expected_attributes,
      yaml_node = yaml_node
    )
    actual = UnambiguousAttributes.parse(yaml_node)
    self.assertEqual(expected, actual)

  def test_wrapped_multiple_attributes(self):
    yaml_node = [{'a': 1, 'b': 2}]
    expected_attributes = {
      'a': AttributeValue(value = 1, yaml_node = 1),
      'b': AttributeValue(value = 2, yaml_node = 2)
    }
    expected = UnambiguousAttributes(
      attributes = expected_attributes,
      yaml_node = yaml_node
    )
    actual = UnambiguousAttributes.parse(yaml_node)
    self.assertEqual(expected, actual)


class TestEmptyElement(ParserRendererTest):

  def test_no_attributes_null(self):
    self.check_rendering(EmptyElement, 'hr:', '<hr>')

  def test_one_attribute(self):
    yaml_src = '''
      hr:
        width: 75%'''
    self.check_rendering(
      EmptyElement,
      yaml_src,
      '<hr width="75%">'
    )

  def test_multiple_attributes(self):
    yaml_src = '''
      link:
        rel: stylesheet
        type: text/css
        href: styles.css'''
    self.check_rendering(
      EmptyElement,
      yaml_src,
      '<link href="styles.css" rel="stylesheet" type="text/css">'
    )

  def test_preferred_render_style_block(self):
    self.assertEqual(
      EmptyElement.parse_yaml('hr:').preferred_render_style(),
      RENDER_BLOCK
    )

  def test_preferred_render_style_inline(self):
    self.assertEqual(
      EmptyElement.parse({'img': {'src': 'header.png'}}).preferred_render_style(),
      RENDER_INLINE
    )

  def test_RENDER_ACCORDING_TO_CHILDREN(self):
    self.assertEqual(
      EmptyElement.parse_yaml('script: ').preferred_render_style(),
      RENDER_INLINE
    )


class TestElementWithContent(ParserRendererTest):

  def test_content_is_singleton_null(self):
    self.check_rendering(
      ElementWithContent,
      'p:\n  -',
      '<p></p>'
    )

  def test_content_is_empty_list(self):
    self.check_rendering(
      ElementWithContent,
      'p: []',
      '<p></p>'
    )

  def test_no_content_just_attributes(self):
    self.check_rendering(
      ElementWithContent,
      '''p:
          - - class: box
              id: the-box
      ''',
      '<p class="box" id="the-box"></p>'
      )

  def test_content_no_attributes(self):
    self.check_rendering(
      ElementWithContent,
      '''p:
          - content
          - more content
      ''',
      '<p>content more content</p>'
    )

  def test_content_is_just_text(self):
    self.check_rendering(
      ElementWithContent,
      'p: some text',
      '<p>some text</p>'
    )

  def test_content_is_unescaped_text(self):
    self.check_rendering(
      ElementWithContent,
      '''p:
        - - escaped & text''',
      '<p>escaped &amp; text</p>'
    )

  def test_nested_content(self):
    self.check_rendering(
      ElementWithContent,
      '''
      html:
       - - lang: en
       - head:
          - title: Hello, world!
       - body:
          - h1: Hello, world!
          - This is my first web page.
      ''',
      ('<html lang="en">\n'
       '  <head>\n'
       '    <title>Hello, world!</title>\n'
       '  </head>\n'
       '  <body>\n'
       '    <h1>Hello, world!</h1>\n'
       '    This is my first web page.\n'
       '  </body>\n'
       '</html>')
    )

  def test_preferred_render_style_block(self):
    self.assertEqual(
      ElementWithContent.parse_yaml('p: some text').preferred_render_style(),
      RENDER_BLOCK
    )

  def test_preferred_render_style_inline(self):
    self.assertEqual(
      ElementWithContent.parse_yaml('i: some text').preferred_render_style(),
      RENDER_INLINE
    )

  def test_preferred_render_style_according_to_children_inline_content(self):
    self.assertEqual(
      ElementWithContent.parse_yaml('ins:\n  - text\n  - more text').preferred_render_style(),
      RENDER_INLINE
    )

  def test_preferred_render_style_according_to_children_block_content(self):
    self.assertEqual(
      ElementWithContent.parse_yaml('ins:\n - p: text').preferred_render_style(),
      RENDER_BLOCK
    )


class TestText(ParserRendererTest):

  def test_bad_text(self):
    node = {'bad': 'node'}
    expected = NotParsed(message = 'Text: not a valid text node', yaml_node = node)
    actual = Text.parse(node)
    self.assertEqual(expected, actual)

  def test_literal(self):
    self.check_rendering(
      Text,
      'literal & text',
      'literal & text'
    )

  def test_escapable_escaping(self):
    self.check_rendering(
      Text,
      '- foo & bar',
      'foo &amp; bar'
    ) 

  def test_markdown(self):
    self.check_rendering(
      Text,
      '- foo',
      '<p>foo</p>',
      markdown = True
    )



class TestEscapableText(ParserRendererTest):

  def test_bad_text(self):
    node = {'bad': 'node'}
    expected = NotParsed(
      message = 'EscapableText: not a singleton list',
      yaml_node = node
    )
    actual = EscapableText.parse(node)
    self.assertEqual(expected, actual)

  def test_escaping(self):
    self.check_rendering(
      EscapableText,
      '- foo & bar',
      'foo &amp; bar'
    )

  def test_markdown(self):
    self.check_rendering(
      EscapableText,
      ('''- |
        Markdown Text
        =============
        
        Markdown --- a "humane" document format.
      '''),
      (
        '<h1>Markdown Text</h1>\n'
        '\n'
        '<p>Markdown &#8212; a &#8220;humane&#8221; document format.</p>'
      ),
      markdown = True,
      markdown_extras = ['smarty-pants']
    )

  def test_preferred_render_style_normal(self):
    self.assertEqual(
      EscapableText.parse(['']).preferred_render_style(),
      RENDER_INLINE
    )

  def test_preferred_render_style_markdown(self):
    self.assertEqual(
      EscapableText.parse(['']).preferred_render_style(markdown = True),
      RENDER_BLOCK
    )



class TestElement(ParserRendererTest):

  def test_bad_element(self):
    node = 'bad node'
    expected = NotParsed(message = 'Element: not a valid element', yaml_node = node)
    actual = Element.parse(node)
    self.assertEqual(expected, actual)

  def test_empty_self_closing_element(self):
    self.check_rendering(
      Element,
      'hr:',
      '<hr>'
    )

  def test_empty_closed_element(self):
    self.check_rendering(
      Element,
      'p: []',
      '<p></p>'
    )

  def test_self_closing_element_with_attribute(self):
    self.check_rendering(
      Element,
      'hr: {width: 75%}',
      '<hr width="75%">'
    )

  def test_closed_element_with_attribute(self):
    self.check_rendering(
      Element,
      'div: [[class: content]]',
      '<div class="content"></div>'
    )

  def test_closed_element_with_text(self):
    self.check_rendering(
      Element,
      'p: Hello, world!',
      '<p>Hello, world!</p>'
    )

  def test_closed_element_with_content(self):
    self.check_rendering(
      Element,
      ('div: \n'
       '  - - class: content\n'
       '  - Some content that wraps\n'
       '    across multiple lines.\n'
       '  - p: A child element.\n'),
      ('<div class="content">\n'
       '  Some content that wraps across multiple lines.\n'
       '  <p>A child element.</p>\n'
       '</div>')
    )


class TestNode(ParserRendererTest):
  
  def test_literal(self):
    self.check_rendering(
      Node,
      'literal & text',
      'literal & text'
    )

  def test_escapable_text(self):
    self.check_rendering(
      Node,
      '- escapable & text',
      'escapable &amp; text',
      markdown = False
    )

  def test_empty_element(self):
    self.check_rendering(
      Node,
      '''img:
           src: pic.gif
           width: 100px
           height: 100px
      ''',
      '<img height="100px" src="pic.gif" width="100px">'
    )

  def test_element_with_content(self):
    self.check_rendering(
      Node,
      'p: content',
      '<p>content</p>',
      markdown = False
    )

  def test_bad_node(self):
    expected = NotParsed(
      message = 'Node: not a valid HTML node',
      yaml_node = []
    )
    actual = Node.parse([])
    self.assertEqual(expected, actual)


class TestNodes(ParserRendererTest):

  # Most of these tests are the same as for Node,
  # except that 'Node' is replaced with 'Nodes'.
  def test_literal(self):
    self.check_rendering(
      Nodes,
      '- literal & text',
      'literal & text'
    )

  def test_escapable_text(self):
    self.check_rendering(
      Nodes,
      '- - escapable & text',
      'escapable &amp; text'
    )

  def test_empty_element(self):
    self.check_rendering(
      Nodes,
      '''img:
          src: pic.gif
          width: 100px
          height: 100px''',
      '<img height="100px" src="pic.gif" width="100px">'
    )

  def test_element_with_content(self):
    self.check_rendering(
      Nodes,
      'p: content',
      '<p>content</p>'
    )

  def test_bad_node(self):
    expected = NotParsed(
      message = 'Node: not a valid HTML node',
      yaml_node = 99 
    )
    actual = Nodes.parse([99])
    self.assertEqual(expected, actual)

  def test_list_of_nodes(self):
    self.check_rendering(
      Nodes,
      (
        '- <!DOCTYPE html>\n'
        '- html:\n'
        '  - - lang: en\n'
        '  - head:\n'
        '     - title: Test page\n'
        '  - body:\n'
        '    - h1: Test page\n'
        '    - p:\n'
        '      - Here is some content\n'
        '        wrapped across a few lines.\n'
        '      - a:\n'
        '         - - href: www.example.com\n'
        '         - Here\'s a link.\n'
        '         - Notice that this is all rendered inline.\n'
        '    - p:\n'
        '      - But if we put in a horizontal rule.\n'
        '      - hr:\n'
        '      - It triggers a change in the rendering style.\n'
      ),
      (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '  <head>\n'
        '    <title>Test page</title>\n'
        '  </head>\n'
        '  <body>\n'
        '    <h1>Test page</h1>\n'
        '    <p>Here is some content wrapped across a few lines. '
        '<a href="www.example.com">Here\'s a link. '
        'Notice that this is all rendered inline.</a></p>\n'
        '    <p>\n'
        '      But if we put in a horizontal rule.\n'
        '      <hr>\n'
        '      It triggers a change in the rendering style.\n'
        '    </p>\n'
        '  </body>\n'
        '</html>'
      )
    )

  def test_preferred_render_style_empty(self):
    self.assertEqual(Nodes.parse([]).preferred_render_style(), RENDER_INLINE)

  def test_preferred_render_style_singleton_literal(self):
    self.assertEqual(Nodes.parse('').preferred_render_style(), RENDER_INLINE)

  def test_preferred_render_style_singleton_text(self):
    self.assertEqual(
      Nodes.parse([['']]).preferred_render_style(),
      RENDER_INLINE
    )

  def test_preferred_render_style_singleton_markdown(self):
    self.assertEqual(
      Nodes.parse([['']]).preferred_render_style(markdown = True),
      RENDER_BLOCK
    )

  def test_preferred_render_style_multi_literals(self):
    self.assertEqual(
      Nodes.parse([[''], ['']]).preferred_render_style(),
      RENDER_INLINE
    )

  def test_preferred_render_style_mixed(self):
    self.assertEqual(
      Nodes.parse([[''], {'p': 'content'}]).preferred_render_style(),
      RENDER_BLOCK
    )

  def test_len(self):
    self.assertEqual(len(Nodes(nodes = ['a', 'b', 'c'])), 3)

  def test_get_item(self):
    self.assertEqual(Nodes(nodes = ['a', 'b', 'c'])[1], 'b')

  def test_iter(self):
    self.assertEqual(list(Nodes(nodes = [1, 2, 3])), [1, 2, 3])



def load_tests(loader, tests, ignore):
  tests.addTests(doctest.DocTestSuite(htyaml))
  return tests