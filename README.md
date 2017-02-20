# django-chemtrails

[![Build Status](https://travis-ci.org/inonit/django-chemtrails.svg?branch=master)](https://travis-ci.org/inonit/django-chemtrails)
[![Coverage Status](https://coveralls.io/repos/github/inonit/django-chemtrails/badge.svg?branch=master)](https://coveralls.io/github/inonit/django-chemtrails?branch=master)

Neo4j based permission backend for Django.

**BIG FAT WARNING**

This is experimental software in a really, really early pre-alpha phase.
Please don't use for anything whatsoever!

Really... please don't ;)


# What's all the fuzz about?
Who doesn't love graphs, charts and visual data? Right, nobody!

This project springs from another project I'm working on which involves a rather complex permission system. As a solution I'm looking into using a graph to help determine if a user has permissions to perform some action on an object, based on the relationship the user has with the object in question.

## Alright... that's stupid!
No it's not! ..or maybe. I don't know yet..

## So...
All I've got is this image...

![The Bookstore graph](/docs/_static/example-graph.png?raw=true "The Bookstore graph")
