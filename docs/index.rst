============================
Chemtrails - Graphing Django
============================

.. image:: _static/chemtrails_bw.png
    :alt: Mind control, no doubt!


.. toctree::
   :maxdepth: 2
   :caption: Table of Contents:
   :name: mastertoc

   01_configuration
   02_contrib_permissions

About
=====

This project aims to solve complex object based permissions by utilizing the relationships
between entities in a graph.

Features
========

    - Synchronize Django model instances to Neo4j
    - Recursively connect related nodes

Installation
============

.. code-block:: none

    $ pip install django-chemtrails

Requirements
============

    - Python 3.5 or 3.6
    - A project running Django 1.10.x or 1.11.x
    - Neo4j running and accepting connections using the bolt protocol

Changelog
=========

v0.0.24
-------

*Release date: 2017-10-09*

    - Workaround fix for `#46 <https://github.com/inonit/django-chemtrails/issues/46>`_. This let's us
      perform ``get_users_with_perms()`` by evaluating queries using the ``"{source}.<attr>"`` syntax, by simply
      ignore the filter.

v0.0.23
-------

*Release date: 2017-10-09*

    - Fixed bug which caused ``AttemptedCardinalityViolation`` when pointing on a new object
      using ``OneToOneField``.
    - Removed support for Django REST Framework compat functions (removed upstreams).

v0.0.22
-------
*Release date: 2017-10-05*

    - Added support for overriding default direction for relationships in access rules.
    - Implemented ``get_users_with_perms()`` function which returns a user queryset which has
      a certain set of permissions for an object.
    - Fixed issue where models listed in ``IGNORE_MODELS`` where synced by related nodes.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
