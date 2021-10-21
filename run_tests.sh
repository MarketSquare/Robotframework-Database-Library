#!/bin/bash -xe

function startup {
    docker-compose up -d 
    sleep 10
}

function cleanup {
    docker-compose down
}

if [[ $1 == "clean" ]]
then
    trap cleanup EXIT
    startup
    sleep 10
fi

export MYSQL_PORT=`docker-compose port mysqldb 3306 | cut -d ":" -f 2`
export POSTGRESQL_PORT=`docker-compose port postgresqldb 5432 | cut -d ":" -f 2`
export DB2_PORT=`docker-compose port db2db 50000 | cut -d ":" -f 2`

yq e -i '
  .MYSQL_DBPort = env(MYSQL_PORT) | 
  .POSTGRESQL_DBPort = env(POSTGRESQL_PORT) |
  .DB2_DBPort = env(DB2_PORT)
' test/DB_Variables.yaml


robot --randomize none -V test/DB_Variables.yaml -i main test
