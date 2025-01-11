
# ON HOST MACHINE
## First run
NEED to set DH_HOST on .env
python run.py

## Consequent runs
python manage.py runserver


# USING DOCKER CONTAINER
docker-compose build
docker-compose up

### OR

docker-compose up --build

## To restart the build the database has to be cleared, to do so
docker-compose down -v