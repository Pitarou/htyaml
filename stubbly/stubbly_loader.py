
import yaml
from .node_graph_filter import scalars_to_strings

def load(yaml_src):
  loader = yaml.Loader(yaml_src)
  loader.check_node()
  node = loader.get_node()
  filtered = scalars_to_strings(node)
  if isinstance(filtered, yaml.MappingNode):
    constructor = loader.construct_mapping
    return loader.construct_mapping(filtered, deep = True)
  if isinstance(filtered, yaml.SequenceNode):
    return loader.construct_sequence(filtered, deep = True)
  if isinstance(filtered, yaml.ScalarNode):
    return loader.construct_scalar(filtered)
  raise TypeError('scalars_to_strings returned a node that is neither MappingNode, SequenceNode, nor Scalar Node')
