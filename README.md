# web_poker
django poker web-app  
<<<<<<< HEAD
prerequisites: docker, python 3.x, pip, git
=======
prerequisites: docker, python 3.x, pip
>>>>>>> e3d043cbe1a73b8454c46e8fcd98d7786c2ff0f6

Installation  
> pip install pipenv  
git clone https://github.com/ZY-KY/web_poker.git  
cd web_poker  
<<<<<<< HEAD
pipenv install -r requirements.txt  

> python manage.py shell  
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()  

copy that to SECRET_KEY = '\<secret key\>' in settings.py  

> docker run -p 6379:6379 -d redis:2.8  
python manage.py migrate  
python manage.py createsuperuser  

to start dev server - takes same parameters as runserver  
=======
pipenv shell  
pipenv install -r requirements.txt  

> docker run -p 6379:6379 -d redis:2.8  
python manage.py makemigrations  
python manage.py migrate  
python manage.py createsuperuser  

to start dev server locally (127.0.0.1:8000) - takes same parameters as runserver  
>>>>>>> e3d043cbe1a73b8454c46e8fcd98d7786c2ff0f6
> python manage.py startserver  
