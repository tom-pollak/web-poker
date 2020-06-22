[![Build Status](https://travis-ci.com/tom-pollak/web_poker.svg?branch=master)](https://travis-ci.com/tom-pollak/web_poker)
# web_poker
### poker web-app written in django

Check out the website here: [pollakpoker.live](https://www.pollakpoker.live)

Prerequisites: Docker, Docker Compose

to setup locally:
```
docker-compose up --build -d
docker-compose exec db psql -U postgres -c "CREATE DATABASE webpoker"
docker-compose exec web python manage.py migrate
docker-compose down
```

run with:
```
docker-compose up
```
