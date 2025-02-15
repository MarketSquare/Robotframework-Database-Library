# Which tests run automatically in the pipeline?
- Tests from the folder `common_tests` run automatically in the pipeline after pushing in the repository
- The tests in the folder `custom_db_tests` are designed to run locally - they have to be triggered manually. I don't run them at all changes.
- There are some unit tests with pytest, but mostly there are acceptance tests with RF
- See the folder `.github/workflows` 

# Which databases / modules are covered?
- The acceptance tests in the pipeline don't cover all possible DB's - here is a lot of room for improvement
- Running tests locally require DB containers running - see below

# Running tests locally from VS Code / terminal
- Selecting a DB module works via a global variable `GLOBAL_DB_SELECTOR` - set it from VSC or CLI
- Current debug/launch configs are implemented for old LSP plugin - still need to update to Robotcode from Daniel

# Here are some advices for local testing of the library with different Python DB modules
## Oracle:
- https://github.com/gvenzl/oci-oracle-free
- https://hub.docker.com/r/gvenzl/oracle-free
- docker pull gvenzl/oracle-free
- docker run --rm --name oracle -d -p 1521:1521 -e ORACLE_PASSWORD=pass -e ORACLE_DATABASE=db -e APP_USER=db_user -e APP_USER_PASSWORD=pass gvenzl/oracle-free

## PostgreSQL
- https://hub.docker.com/_/postgres
- docker pull postgres
- docker run --rm --name postgres -e POSTGRES_USER=db_user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=db -p 5432:5432 -d postgres

## Teradata
- use VM image, e.g. in VirtualBox
- https://downloads.teradata.com/download/database/teradata-express/vmware
- use network bridge mode
- create new DB
    CREATE DATABASE db
    AS PERMANENT = 60e6, -- 60MB
        SPOOL = 120e6; -- 120MB
- Install Teradata driver for your OS
    https://downloads.teradata.com/download/connectivity/odbc-driver/windows

- DEPRECATED: https://github.com/teradata/PyTd
    -> new: https://github.com/Teradata/python-driver
- docs: https://quickstarts.teradata.com/getting.started.vbox.html

## IBM Db2
- https://hub.docker.com/r/ibmcom/db2
- docker pull ibmcom/db2
- docker run --rm -itd --name mydb2 --privileged=true -p 50000:50000 -e LICENSE=accept -e DB2INSTANCE=db_user -e DB2INST1_PASSWORD=pass -e DBNAME=db ibmcom/db2
--> needs some minutes to start the DB !!!

## MySQL
- https://hub.docker.com/_/mysql
- docker run --rm --name mysql -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=db -e MYSQL_USER=db_user -e MYSQL_PASSWORD=pass -p 3306:3306 -d mysql
- For tests with pyodbc install the ODBC driver https://learn.microsoft.com/en-us/sql/connect/odbc/windows/system-requirements-installation-and-driver-files?view=sql-server-ver16#installing-microsoft-odbc-driver-for-sql-server

## Microsoft SQL Server
- https://hub.docker.com/_/microsoft-mssql-server
- docker run --rm --name mssql -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD='MyPass1234!' -p 1433:1433 -d mcr.microsoft.com/mssql/server
--> login and create DB:
    - docker exec -it mssql bash
    - /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'MyPass1234!'
    - CREATE DATABASE db
    - go
- docs: https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-ver16&pivots=cs1-bash