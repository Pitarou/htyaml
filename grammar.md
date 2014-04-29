Text is text, but with entity escaping.

> *YAML:* `Hello & world!`
>
> *Python:* `'Hello & world!'`
>
> *Rendered HTML:* `Hello &amp; world!`

With `markdown = True`, text is passed through the Markdown2 interpreter,
rather than just being escaped. Pass extra options to the Markdown2 interpreter
with the `markdown_extras` option.

    >>> text = 'Markdown -- a "humane" document format'
    >>> parsed = HTYAML.parse_yaml(text)
    >>> print(parsed.render(
    ...   markdown = True,
    ...   markdown_extras = ['smarty-pants'] # smarten up quotes and hyphens
    ... ))
    <p>Markdown &#8212; a &#8220;humane&#8221; document format</p>

If you get a yaml parsing error, check that your text is not being interepreted
as a non-textual object. Strings like '`null`', '`yes`', '`on`', '`42`'
or anything containing the sequence `': '` can cause problems.
To avoid this, wrap the text in quotes.

> *YAML:* `- "This colon: would cause problems without the quotes."

An html element is represented as a singleton dict. The simplest case is
an element that has no content or closing element, and no elements.

> *YAML:* `hr:`
> 
> *Python:* `{'hr': None}`
> 
> *Rendered HTML:* <hr>

An attributes dict can be added.

> *YAML:*
> 
>     img:
>         src: http://placekitten.com/200/300
>         width: 200px
>         height: 300px
>
> *Python:*
> 
>     {
>       'img': {
>         'src': 'http://placekitten.com/200/300',
>         'width': '200px',
>         'height': '300px',
>       }
>     }
> 
> *Rendered HTML:*
> 
>     <img height="300px" src="http://placekitten.com/200/300" width="200px">

Notice that the attributes are rendered in alphabetical order. This consistent
ordering helps with unit testing.

As a kind of shorthand, for elements with just a single item of text content
and no attributes, the text content can be included directly in the dict.

> *YAML*:  `em: emphatically`
>
> *Python*: `{'em': 'emphatically'}`
>
> *Rendered HTML*: `<em>emphatically</em>`

But in all other cases, the element's content is represented as a list.

> *YAML:*
> 
>     div:
>       - Content.
>       - hr:
>           width: 75%
>       - Footnotes.
>
> *Python:*
>   
>     {
>       'div': [
>         'Content.',
>         {'hr': {'width': '75%'}},
>         'Footnotes',
>       ]
>     }
>
> *Rendered HTML:*
> 
>     <div>
>       Content.
>       <hr width="75%">
>       Footnotes.
>     </div>

If the first entry of the list of content is a dict with zero entries,
or more than one entry, it is treated as an attribute list.
(If it has one entry, it is treated as an element.)

> *YAML:*
>
>     div:
>       - width: 200px
>         height: 300px
>         style: place-kitten
>       - Can haz pleis?
>
> *Python:*
>
>     {
>       'div': [
>         {
>           'width': '200px',
>           'height': '300px',
>           'style': 'place-kitten',
>         },
>         'Can haz pleis?',
>       ]
>     }
>
> *HTML:*
>
>     <div height="300px" style="place-kitten" width="200px">
>       Can haz pleis?
>     </div>

An attribute list can be "escaped" by wrapping it in singleton list.
This allows you to add a single attribute:

> *YAML:*
>
>     div:
>       - - class: place-kitten
>       - p: Can haz pleis?
>
> *Python:*
>
>     {
>       'div': [
>         [{'class': 'place-kitten'}],
>         {'p': 'Can haz pleis?'},
>       ]
>     }
>
> *HTML:*
>
>     <div class="place-kitten">
>       <p>Can haz pleis?</p>
>     </div>

Another way to add a single attribute is by adding a 'null' attribute
to the list, which is represented in YAML by a `?`. This will be
discarded by the parser:

> *YAML:*
>
>     div:
>       - class: place-kitten
>         ?
>       - Can haz pleis?
>
> *Python:*
>
>      {
>        'div': [
>          {
>            'class': 'place-kitten',
>            None: None,
>          },
>          'Can haz pleis?',
>        ]
>      }
>
> *HTML:*
>
>     <div class="place-kitten">
>       <p>Can haz pleis?</p>
>     </div>


Similarly, literal text is escaped by wrapping it in a list.

> *YAML:*
>
>   div:
>    - This is automatically & escaped.
>    - - I hand escaped &amp; this one.
>
> *Python:*
>
>   {
>     'div': [
>       'This is automatically & escaped.',
>       ['I hand escaped &amp; this one.'],
>     ]
>   }
>
> *HTML:*
>
>   <div>
>     This is automatically &amp; escaped.
>     I hand escaped &amp; this one.
>   </div>