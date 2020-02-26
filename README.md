# web_poker
django poker web-app  
prerequisites: docker, python 3.x, pip, git

Installation  
> pip install pipenv  
git clone https://github.com/ZY-KY/web_poker.git  
cd web_poker  
pipenv install -r requirements.txt  

> python manage.py shell  
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()  

copy that to SECRET_KEY = '\<secret key\>' in settings.py  

> docker run -p 6379:6379 -d redis:2.8  
python manage.py migrate  
python manage.py createsuperuser  

to start dev server - takes same parameters as runserver  
> python manage.py startserver  
