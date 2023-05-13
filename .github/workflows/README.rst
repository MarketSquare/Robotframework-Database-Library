Test Framework for the DatabaseLibrary using Github Actions
===========================================================

.. contents::

!! Work In Progress !!
----------------------
Note at this time this GitHub Actions CI workflow is a work in progress. I've been trying
to build a "complete" set of database and databse module suites. This notes, which are also
a work in progress, are here to help guide you and remind us of where we are at.

About this test framework
-------------------------
As I re-exmine using GitHub Actions and expanding the internal test suite, I am reminded
of why creating a test suite with GitHub Actions has been difficult. The number of modules
currently supported (by code) is between nine and twelve. The number of databases known to
be supported by Python is over thirty. So the possibly test matrix for the library is very,
very, large.

Given the possibilities we will start with looking from the perspective of Python modules
(as compared to databases) and limit it to those nine currently supported by test code.

Database Systems and Python Modules
----------------------------

There are a variety of database systems and Python modules that the DatabaseLibrary supports. This
chart is intended to keep track of those implemented and resources around them.


==================================  ===========  ==========================  =======================================
    Database Systems                    module       Status                      Workflow
==================================  ===========  ==========================  =======================================
MySQL                               pymysql      Completed                   MySQL-tests.yml
\                                   pyodbc       Completed                   MySQL-tests.yml
PostgreSQL                          psycopg2     Completed                   PostgreSQL-tests.yml
\                                   psycopg3     Not Yet Implemented
\                                   pyodbc       Not Yet Implemented
SQLite                              sqlite3      Completed                   SQLite-tests.yml
==================================  ===========  ==========================  =======================================


==================================  ===========  ==========================  =======================================
    Database                            module       ..something..               Comment
==================================  ===========  ==========================  =======================================
Sub-Etha                            h2g2                                     The Hitchhiker's Database to the Galaxy
==================================  ===========  ==========================  =======================================


References:

`PEP 249 - Python Database API Specification v2.0<https://peps.python.org/pep-0249/>`_

`Database interfaces available for Python<https://wiki.python.org/moin/DatabaseInterfaces>`_