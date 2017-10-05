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

v0.0.20
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
