## Requirements
   - Python3.x and pip installed

## Install

##### Install unixodbc driver

To install ```pyodbc``` (module to access ODBC databases), is necessary install ```unixodbc``` in the OS:

 - In Mac:
``` bash
brew install unixodbc
```
 - In Linux:
``` bash
sudo apt-get update -y && sudo apt-get install -y unixodbc-dev
```

##### Set up python virtual environment

Create python 3 environment:
```
pip install pipenv
pipenv install && pipenv install --dev
```

Install GitHooks
```
pipenv shell
pipenv install pre-commit install
```

Activate environment:
```
pipenv shell
```

If error in mac to install dependencies
```
env ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install cryptography
```
### Without Pipenv
If you want create a virtualenv without pipenv, you can generate requirements.txt running follow line:
``` bash
pip install pipfile-requirements && pipfile2req > requirements.txt && pipfile2req --dev >> requirements.txt
```

## MongoDB

db and the collection is created automatically

## Azure SAS

In order to generate the SAS, it is assumed that the cloud_service table has a cloud_name with "Azure" associated with the user's company.

## Run

```
./script/run.sh
```

## Run Automatic Test

Running tests require some previous setup, see documentation [here](test/README.md)

---
## Project structure

```
|- api  
|- app  
|- core  
|- db  
|- models  
|- schemas  
|- scripts  
|- test  
```
