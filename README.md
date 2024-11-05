# luxehorizon
for installing the dependencies of this project run the following command 
pip install -r requirements.txt

# connect to the database
clone the .env.example to a .env flie and place it on the root of the project
replace all the placeholders to the right values

# if you make changes on the models please run: 
python manage.py makemigrations

# everytime you enter the project and there are new migrations please run 
python manage.py migrate