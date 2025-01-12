
# ON HOST MACHINE
## Before starting the project app
A postgresql and mongodb database need to be installed and configured.
As well as python.
## First run
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

## Consequent runs
`python manage.py runserver`


# USING DOCKER CONTAINER
`docker-compose build`
`docker-compose up`

### OR

`docker-compose up --build`

## To restart the build and clear the database
`docker-compose down -v`


## Complete clean build commands
docker-compose down -v --remove-orphans
docker-compose build --no-cache
docker-compose up --force-recreate


