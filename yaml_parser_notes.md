Notes on the YAML parser

According to the YAML spec, the YAML parsing pipeline looks like this:

> Presentation (CharacterStream)
> 
> &darr;
> *Parse*
> &darr;
>
> Serialization (Event Tree)
>
> &darr;
> *Compose*
> &darr;
>
> Representation (Node Graph)
>
> &darr;
> *Construct*
> &darr;
>
> Native (Data Structure)

The node graph contains three kinds of nodes: scalar, sequence and mapping.

Scalar nodes contain a string, and a tag indicating the type.  For instance,
if the parser sees '42', it emits:

>     ScalarNode(tag='tag:yaml.org,2002:int', value='42')

It looks like it checks the string against a list of regular expressions, and only
emits `tag='tag:yaml.org,2002:str'` if none of them match. It's possible to add
something to the end of the list of expressions, but not to the beginning.
So if something is recognised as, say, an int, there's no way to override this.

However, it's possible for me to add my own filter that modifies the node graph.
The specification for the node graph is admirably clear and simple, so it looks
quite easy to do.