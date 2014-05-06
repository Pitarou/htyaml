# html.escape superseded cgi.escape in Python 3.2.
#
# As far as I know, they both work the same so long
# as you are explicit about the optional `quote`
# argument.
from sys import hexversion
if hexversion >= 0x03020000:
  from html import escape
else:
  from cgi import escape


[
  RENDER_INLINE,
  RENDER_BLOCK,
  RENDER_ACCORDING_TO_CHILDREN,
] = [
  'render inline',
  'render block',
  'render according to children',
]

elements_rendered_inline = [
  'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'cite',
  'code', 'dfn', 'em', 'i', 'img', 'input', 'kbd', 'label',
  'q', 'samp', 'select', 'small', 'span', 'strong',
  'sub', 'sup', 'textarea', 'tt', 'var'
]

elements_rendered_according_to_children = [
  'button', 'del', 'ins', 'map', 'object', 'script'
]

elements_rendered_block = [
  'address', 'article', 'aside', 'audio', 'blockquote', 'br', 'canvas', 'dd', 
  'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2',
  'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr', 'li', 'noscript', 'ol',
  'output', 'p', 'pre', 'section', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
  'tr', 'ul', 'video'
]

kwarg_defaults = {
  'markdown': False,
  'line_prefix': '',
  'markdown_extras': [],
  'unknown_element_render_style': RENDER_BLOCK,
}

_render_style_table_suffix = '_render_style'
for (tags, render_style) in (
  (elements_rendered_inline, RENDER_INLINE),
  (elements_rendered_according_to_children, RENDER_ACCORDING_TO_CHILDREN),
  (elements_rendered_block, RENDER_BLOCK),
):
  for tag in tags:
    kwarg_defaults[tag + _render_style_table_suffix] = render_style

def get_kwarg_with_default(kwargs, arg_name, not_found = None):
  return kwargs[arg_name] if arg_name in kwargs else kwarg_defaults[arg_name]

def get_tag_render_style(kwargs, tag):
  kwarg = tag.lower() + _render_style_table_suffix
  try:
    return get_kwarg_with_default(kwargs, kwarg)
  except KeyError:
    return get_kwarg_with_default(kwargs, 'unknown_element_render_style')
