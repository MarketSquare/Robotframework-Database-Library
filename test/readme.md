# Some tests are run automatically in the pipeline after pushing in the repository
See the folder `.github/workflows` 
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
- docker run --rm --name mssql -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=MyPass1234!" -p 1433:1433 -d mcr.microsoft.com/mssql/server
--> login and create DB:
    - docker exec -it mssql bash
    - /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'MyPass1234!'
    - CREATE DATABASE db
    - go
- docs: https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-ver16&pivots=cs1-bash