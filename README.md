A YAML+Markdown &rarr; HTML parser.

HTML is ugly, but YAML and Markdown are pretty, so lets use them.

For instance this:

    - - <!DOCTYPE html>
    - html:
       - - lang: en
       - head:

          - meta:
             charset: utf-8

          - meta:
             http-equiv: X-UA-Compatible
             content: IE=edge

          - meta:
             name: viewport
             content: width=device-width, initial-scale=1
  
          - link:
             rel: stylesheet
             href: //netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css

          - title: [[Bootstrap 101 Template]]

       - body:
          - div:
             - - class: jumbotron

             - |
                 Hello, world!
                 =============

                 This is a simple hero unit, a simple jumbotron-style
                 component for calling extra attention to featured content
                 or information.

                 <a class="btn btn-primary btn-lg">Learn more</a>

          - script:
             type: text_javascript
             src: js/bootstrap.min.js

Gets rendered (with the markdown option) as:

    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta content="IE=edge" http-equiv="X-UA-Compatible">
        <meta content="width=device-width, initial-scale=1" name="viewport">
        <link href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" rel="stylesheet">
        <title>Bootstrap 101 Template</title>
      </head>
      <body>
        <div class="jumbotron">
          <h1>Hello, world!</h1>

          <p>This is a simple hero unit, a simple jumbotron-style
          component for calling extra attention to featured content
          or information.</p>

          <p><a class="btn btn-primary btn-lg">Learn more</a></p>
        </div>
        <script src="js/bootstrap.min.js" type="text_javascript">
      </body>
    </html>

There's still a lot of work to do before this can be used for rendering web pages,
including:

 - refine the syntax (in particular, I want to swap the literal text
   with the unescaped text)
 - add moustache support