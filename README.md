# django-chemtrails

[![Build Status](https://travis-ci.org/inonit/django-chemtrails.svg?branch=master)](https://travis-ci.org/inonit/django-chemtrails)
[![Coverage Status](https://coveralls.io/repos/github/inonit/django-chemtrails/badge.svg?branch=master)](https://coveralls.io/github/inonit/django-chemtrails?branch=master)
[![Documentation Status](https://readthedocs.org/projects/django-chemtrails/badge/?version=latest)](http://django-chemtrails.readthedocs.io/en/latest/?badge=latest)

Neo4j based permission backend for Django.

[Documentation available](http://django-chemtrails.rtfd.io/>) on Read the Docs!

**BIG FAT WARNING**

This is experimental software in a really, really early pre-alpha phase.
Please don't use for anything whatsoever!

Really... please don't ;)


# What's all the fuzz about?
Who doesn't love graphs, charts and visual data? Right, nobody!

This project springs from another project I'm working on which involves
a rather complex permission system. As a solution I'm looking into
using a graph to help determine if a user has permissions to perform
some action on an object, based on the relationship the user has with
the object in question.

## Meta data

<p align="center">
![The Bookstore meta graph](/docs/_static/example-meta-graph.png?raw=true "The Bookstore meta graph")
</p>


## Node data

<p align="center">
![The Bookstore graph](/docs/_static/example-node-graph.png?raw=true "The Bookstore graph")
</p>
