.. _configuration-label:

=============
Configuration
=============

Add ``chemtrails`` to ``INSTALLED_APPS`` in your ``settings.py`` file.

.. code-block:: python

    #
    # settings.py
    #

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        ...
        'chemtrails'
    ]

Chemtrails settings
===================

Settings for ``chemtrails`` are all namespaced in the ``CHEMTRAILS`` setting dictionary.

.. code-block:: python

    #
    # settings.py
    #

    CHEMTRAILS = {
        # Flip the chemtrails-switch. Boolean value to indicate if mind-control fluid should
        # be enabled and data written into the Neo4j database.
        # Defaults to True.
        'ENABLED': True,

        # If True, relationships will be named (loosely) after the attribute name
        # on the Django model. If False, relationships will have a generic name of
        # either 'RELATES_TO', 'RELATES_FROM' or 'MUTUAL_RELATION' based on the relationship type.
        # Defaults to True.
        'NAMED_RELATIONSHIPS': True

        # A list of models that should be excluded from mirroring.
        # Defaults to the example shown below.
        'IGNORE_MODELS': [
            'migrations.migration'
        ]
    }
