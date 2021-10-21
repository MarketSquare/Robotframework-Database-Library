# Robotframework-Database-Library

Database Library contains utilities meant for Robot Framework's usage. This can allow you to query your database after an action has been made to verify the results. This is compatible\* with any Database API Specification 2.0 module.

## Testing

Manualy start databases in docker-compose and then run "main" tests:

```
docker-compose up -d
docker-compose ps

# Update `DB_Variables.yaml` with proper ports

robot -V test/DB_Variables.yaml -i main test
```

Or just leave it all to the small Bash script that will setup docker-compose environment and set proper values to test/DB_Variables.yaml:

```
./run_tests.sh clean
```

If you wish to start only tests without setup docker-compose setup:

```
./run_tests.sh
```
