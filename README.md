# ON HOST MACHINE

### Before starting the project app

A *postgresql* and *mongodb* database need to be installed and configured.
A database user must also be created for each database created in the previous step.
And python must also be installed.

### First run

NEED to set the following variables in an .env file:

- **DB_NAME**=*db_name*

- **DB_USER**=*db_user*

- **DB_PASSWORD**=*db_password*

- **DB_HOST**=*db_host*

- **DB_PORT**=*db_port*

- **DEBUG**=*debug* - (True or False make it False in production)

- **MONGO_INITDB_ROOT_USERNAME**=*mongo_user*

- **MONGO_INITDB_ROOT_PASSWORD**=*mongo_password*

- **MONGO_INITDB_HOST**=*host* - (mongodb on docker or localhost)


Then run:

`python run.py`

  

### Consequent runs

`python manage.py runserver`

  
  

# USING DOCKER CONTAINER
First open a terminal (cmd or powershell) inside the root directory of the project then run the following commands:

`docker-compose build`

`docker-compose up`

### OR


`docker-compose up --build`

  

## To restart the build and clear the database

`docker-compose down -v`

Besides this command, sometimes its needed to make a harder clean by removing builds from the "builds history" `docker builder prune`, as well as deleting local images `docker image prune`.

  
  

## Complete clean build commands

docker-compose down -v --remove-orphans

docker-compose build --no-cache

docker-compose up --force-recreate