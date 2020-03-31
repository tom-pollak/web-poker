# web_poker
django poker web-app  
prerequisites: docker, python 3.x, pip

Installation  
> pip install pipenv  
git clone https://github.com/ZY-KY/web_poker.git  
cd web_poker  
pipenv shell  
pipenv install -r requirements.txt  

> docker run -p 6379:6379 -d redis:2.8  
python manage.py makemigrations  
python manage.py migrate  
python manage.py createsuperuser  

to start dev server locally (127.0.0.1:8000) - takes same parameters as runserver  
> python manage.py startserver  
