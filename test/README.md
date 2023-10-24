## Requirements

* Everything needed for getting the app running, se main README

* Docker engine installed

* Docker Compose tool installed

## Setup

* Set environment variables accordingly:

In scripts/test_env_setup.sh, edit the following variables:

```
export MONGO_SERVER=mongodb://localhost:27017/ \
SQL_DRIVER='{ODBC Driver 17 for SQL Server}' \
SQL_SERVER=127.0.0.1 \
SQL_DATABASE=folpix_test \
SQL_USER=SA \
SQL_PASS=PiData20! \
API_CLIENT_SECRET="supersecretshh"
```

* Run setup:

```
./scripts/test_env_setup.sh
```

## Run tests

In the base folder:
```
./scripts/test.sh
```
