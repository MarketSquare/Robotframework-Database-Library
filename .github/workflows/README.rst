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
MySQL                               pymysql      Completed                   common_tests.yml
\                                   pyodbc       Completed                   common_tests.yml
PostgreSQL                          psycopg2     Completed                   common_tests.yml
\                                   psycopg3     Not Yet Implemented
\                                   pyodbc       Not Yet Implemented
SQLite                              sqlite3      Completed                   common_tests.yml
Oracle - "custom params"            oracledb     Workflow is done,           common_tests.yml
                                                 but some tests are failing
                                                 bugs have to be fixed
                                                 in the library,
                                                 tests are to be checked
                                                 and probably extended
Teradata                            Teradata     Can be tested locally only,    local only
                                                 as it requires a VM
Excel                               pyodbc       Currentyl local tests only,    local only
                                                 as I wasn't able to install
                                                 the ODBC driver for Excel
                                                 in the container
IBM DB2                             ibmdb        Currently local tests only,    local only
                                                 as I wasn't able to get
                                                 the container working in
                                                 the workflow                                                  
==================================  ===========  ==========================  =======================================


==================================  ===========  ==========================  =======================================
    Database                            module       ..something..               Comment
==================================  ===========  ==========================  =======================================
Sub-Etha                            h2g2                                     The Hitchhiker's Database to the Galaxy
==================================  ===========  ==========================  =======================================


References:

`PEP 249 - Python Database API Specification v2.0<https://peps.python.org/pep-0249/>`_

`Database interfaces available for Python<https://wiki.python.org/moin/DatabaseInterfaces>`_

Docker container with Oracle DB: https://github.com/gvenzl/oci-oracle-free
