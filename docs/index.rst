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

    - A Django project
    - Neo4j running and accepting connections using the bolt protocol

Changelog
=========

v0.0.20
-------
*Release date: 2017-10-04*

    - Added support for overriding default direction for relationships in access rules.
    - Implemented ``get_users_with_perms()`` function which returns a user queryset which has
      a certain set of permissions for an object.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
