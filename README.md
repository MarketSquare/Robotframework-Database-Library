# Robotframework-Database-Library

Database Library contains utilities meant for Robot Framework's usage. This can allow you to query your database after an action has been made to verify the results. This is compatible\* with any Database API Specification 2.0 module.

## Testing

```
docker-compose up -d
docker-compose ps

popd test
# Update `DB_Variables.yaml` with proper ports

robot -V DB_Variables.yaml -i standard .

# or just
./run_tests.sh

pushd
```
