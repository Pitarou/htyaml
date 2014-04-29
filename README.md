A YAML+Markdown &rarr; HTML parser.

HTML is ugly, but YAML and Markdown are pretty, so lets use them.

For instance this:

    - <!DOCTYPE html>

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

          - title: Bootstrap Jumbotron Example

       - body:

          - div:
             - - class: jumbotron

             - - |
                 Hello, world!
                 =============

                 This is a simple hero unit, a simple jumbotron-style
                 component for calling extra attention to featured content
                 or information.

             - a:
                - - class: btn btn-primary btn-lg
                - Learn more

          - script:
             type: text_javascript
             src: js/bootstrap.min.js

Gets rendered (with the Markdown option) as:

    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta content="IE=edge" http-equiv="X-UA-Compatible">
        <meta content="width=device-width, initial-scale=1" name="viewport">
        <link href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" rel="stylesheet">
        <title>Bootstrap Jumbotron Example</title>
      </head>
      <body>
        <div class="jumbotron">
          <h1>Hello, world!</h1>

          <p>This is a simple hero unit, a simple jumbotron-style
          component for calling extra attention to featured content
          or information.</p>
          <a class="btn btn-primary btn-lg">Learn more</a>
        </div>
        <script src="js/bootstrap.min.js" type="text_javascript">
      </body>
    </html>

Before this system is fit for real-world use, it needs some kind of templating
support. A moustache-style rendering system would seem a natural choice.