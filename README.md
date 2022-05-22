[![Build Status](https://travis-ci.com/tom-pollak/web_poker.svg?branch=master)](https://travis-ci.com/tom-pollak/web_poker)
# Web Poker
### poker web-app written in django

Prerequisites: Docker, Docker Compose

to setup locally:
```
docker-compose up --build -d
docker-compose exec db psql -U postgres -c "CREATE DATABASE webpoker"
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py migrate
docker-compose down
```

run with:
```
docker-compose up
```
