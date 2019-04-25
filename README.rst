========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls| |codecov|
        | |landscape| |codeclimate|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |travis| image:: https://travis-ci.org/macisamuele/fog_director_simulator.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/macisamuele/fog_director_simulator

.. |requires| image:: https://requires.io/github/macisamuele/fog_director_simulator/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/macisamuele/fog_director_simulator/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/macisamuele/fog_director_simulator/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/macisamuele/fog_director_simulator

.. |codecov| image:: https://codecov.io/github/macisamuele/fog_director_simulator/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/macisamuele/fog_director_simulator

.. |landscape| image:: https://landscape.io/github/macisamuele/fog_director_simulator/master/landscape.svg?style=flat
    :target: https://landscape.io/github/macisamuele/fog_director_simulator/master
    :alt: Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/macisamuele/fog_director_simulator/badges/gpa.svg
   :target: https://codeclimate.com/github/macisamuele/fog_director_simulator
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/fog-director-simulator.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/fog-director-simulator

.. |commits-since| image:: https://img.shields.io/github/commits-since/macisamuele/fog_director_simulator/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/macisamuele/fog_director_simulator/compare/v0.0.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/fog-director-simulator.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/fog-director-simulator

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/fog-director-simulator.svg
    :alt: Supported versions
    :target: https://pypi.org/project/fog-director-simulator

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/fog-director-simulator.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/fog-director-simulator


.. end-badges

An example package. Generated with cookiecutter-pylibrary.

* Free software: MIT license

Installation
============

::

    pip install fog-director-simulator

Documentation
=============


To use the project:

.. code-block:: python

    import fog_director_simulator
    fog_director_simulator.longest()


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
