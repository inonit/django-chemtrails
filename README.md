# django-chemtrails

[![Code Health](https://landscape.io/github/inonit/django-chemtrails/master/landscape.svg?style=flat)](https://landscape.io/github/inonit/django-chemtrails/master)
[![Build Status](https://travis-ci.org/inonit/django-chemtrails.svg?branch=master)](https://travis-ci.org/inonit/django-chemtrails)
[![Coverage Status](https://coveralls.io/repos/github/inonit/django-chemtrails/badge.svg?branch=master)](https://coveralls.io/github/inonit/django-chemtrails?branch=master)
[![Documentation Status](https://readthedocs.org/projects/django-chemtrails/badge/?version=latest)](http://django-chemtrails.readthedocs.io/en/latest/?badge=latest)

Graphing Django

[Documentation available](http://django-chemtrails.rtfd.io/) on Read the Docs!

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

Currently there is two kind of node types; `MetaNodes` and `ModelNodes`.
The `MetaNodes` contains no user data, but are meant to visualize the
structure of the database. Each node contains meta data such as
`app_label`, `model_name` and so on as well as relations to other
`MetaNodes`. They may also be connected to the actual `ModelNodes` by
flipping on a setting.

The image below displays all the `MetaNodes` for the `Bookstore` app
used to test and develop this library.

![The Bookstore meta graph](/docs/_static/example-meta-graph.png?raw=true "The Bookstore meta graph")


## Node data

`ModelNodes` on the other hand is more of a copy of a model instance.
It contains data from the the actual object, as well as relations to
other nodes.

The image below displays the `ModelNodes` for the `Bookstore` app.

![The Bookstore graph](/docs/_static/example-node-graph.png?raw=true "The Bookstore graph")


# Give it a spin

As stated earlier, for now this project is **not** suitable for any usage,
except fooling around a bit. If you'd like to try it out follow the steps below.

```
$ git clone https://github.com/inonit/django-chemtrails.git
$ cd django-chemtrails
django-chemtrails:$ docker-compose up -d
django-chemtrails:$ python manage.py migrate
django-chemtrails:$ python manage.py testgraph 2  # any number
Hang tight, this might take a little while...
Successfully created 2 bookstore graphs.
Check them out in the Neo4j web console!
```

Open the Neo4j web console at [http://localhost:7474](http://localhost:7474/browser/)
and enter a Cypher query to fetch everything.

```
MATCH (n) RETURN n
```

To wipe out the entire Neo4j database, enter the following Cypher query.

```
MATCH (n) DETACH DELETE n
```
