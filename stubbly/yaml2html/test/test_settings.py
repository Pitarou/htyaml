
from unittest import TestCase
from ..settings import *

class TestKwargWithDefault(TestCase):
  def test_found(self):
    self.assertEqual(get_kwarg_with_default({'a': 1}, 'a'), 1)

  def test_not_found(self):
    self.assertFalse(get_kwarg_with_default({'a': 1}, 'markdown'))

class TestTagRenderStyle(TestCase):
  def test_inline_default(self):
    self.assertEqual(get_tag_render_style({}, 'i'), RENDER_INLINE)

  def test_block_default(self):
    self.assertEqual(get_tag_render_style({}, 'p'), RENDER_BLOCK)
  def test_according_to_children_default(self):
    self.assertEqual(get_tag_render_style({}, 'del'), RENDER_ACCORDING_TO_CHILDREN)

  def test_override_with_kwargs(self):
    self.assertEqual(
      get_tag_render_style({'del_render_style': RENDER_BLOCK}, 'del'),
      RENDER_BLOCK
    )

  def test_not_found(self):
    self.assertEqual(get_tag_render_style({}, 'foo'), RENDER_BLOCK)

  def test_upper_case(self):
    self.assertEqual(
      get_tag_render_style(
        {'foo_render_style': RENDER_INLINE},
        'FOO'
      ),
      RENDER_INLINE
    )

  def test_not_found(self):
    self.assertEqual(
      get_tag_render_style(
        {'unknown_element_render_style': RENDER_ACCORDING_TO_CHILDREN},
        'foo'
      ),
      RENDER_ACCORDING_TO_CHILDREN
    )