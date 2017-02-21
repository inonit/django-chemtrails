# django-chemtrails

[![Build Status](https://travis-ci.org/inonit/django-chemtrails.svg?branch=master)](https://travis-ci.org/inonit/django-chemtrails)
[![Coverage Status](https://coveralls.io/repos/github/inonit/django-chemtrails/badge.svg?branch=master)](https://coveralls.io/github/inonit/django-chemtrails?branch=master)
[![Documentation Status](https://readthedocs.org/projects/django-chemtrails/badge/?version=latest)](http://django-chemtrails.readthedocs.io/en/latest/?badge=latest)

Graphing Django

[Documentation available](http://django-chemtrails.rtfd.io/>) on Read the Docs!

**BIG FAT WARNING**

This is experimental software in a really, really early pre-alpha phase.
The API is guaranteed to change without any notice. Please don't
use for anything whatsoever!


# What's all the fuzz about?
Who doesn't love graphs, charts and visual data?

This project springs from another project I'm working on which involves
a rather complex permission system. As a solution I'm looking into
using a graph to help determine if a user has permissions to perform
some action on an object, based on the relationship between entities.

## Meta data

Currently there is two kind of node types; ``MetaNodes`` and ``ModelNodes``.
The `MetaNodes` contains no user data, but are meant to visualize the
structure of the database. Each node contains meta data such as
``app_label``, ``model_name`` and so on as well as relations to other
`MetaNodes`. They may also be connected to the actual `ModelNodes` by
flipping on a setting.

The image below displays all the ``MetaNodes`` for the `Bookstore`` app
used to test and develop this library.

![The Bookstore meta graph](/docs/_static/example-meta-graph.png?raw=true "The Bookstore meta graph")


## Node data

``ModelNodes`` on the other hand is more of a copy of a model instance.
It contains data from the the actual object, as well as relations to
other nodes.

The image below displays the ``ModelNodes`` for the `Bookstore` app.

![The Bookstore graph](/docs/_static/example-node-graph.png?raw=true "The Bookstore graph")
