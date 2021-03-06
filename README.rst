..
    Copyright (C) 2022 Geo Secretariat.

    geo-rdm-records is free software; you can redistribute it and/or modify
    it under the terms of the MIT License; see LICENSE file for more details.

================
 GEO RDM Records
================

.. .. image:: https://img.shields.io/pypi/dm/geo-rdm-records.svg
..         :target: https://pypi.python.org/pypi/geo-rdm-records

.. image:: https://github.com/geo-knowledge-hub/geo-rdm-records/workflows/CI/badge.svg
        :target: https://github.com/geo-knowledge-hub/geo-rdm-records/actions?query=workflow%3ACI

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/lifecycle-maturing-blue.svg
        :target: https://www.tidyverse.org/lifecycle/#maturing
        :alt: Software Life Cycle

.. image:: https://img.shields.io/github/license/geo-knowledge-hub/geo-rdm-records.svg
        :target: https://github.com/geo-knowledge-hub/geo-rdm-records/blob/master/LICENSE

.. image:: https://img.shields.io/github/tag/geo-knowledge-hub/geo-rdm-records.svg
        :target: https://github.com/geo-knowledge-hub/geo-rdm-records/releases

.. image:: https://img.shields.io/discord/730739436551143514?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/730739436551143514#
        :alt: Join us at Discord

DataCite-based data model for GEO Knowledge Hub flavour.

Development
===========

Install
-------

Install the package with the `docs`, `elasticsearch`, and a `database` dependencies:

.. code-block:: console

    pip install -e .[docs, <[mysql|postgresql|sqlite]>, elasticsearch7]


Tests
-----

After installing the package and its dependencies, if you want to test the code, install the `tests` dependencies:

.. code-block:: console

    pip install -e .[tests]

Now, you can run the tests:

.. code-block:: console

    ./run-tests.sh
