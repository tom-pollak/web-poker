# web_poker
## poker web-app written in django

Check out the website here: [pollakpoker.live](https://www.pollakpoker.live)

Prerequisites: Docker, Docker Compose

to run locally:
```
echo "PORT=8000" > .env
docker-compose up --build -d
docker-compose exec python manage.py migrate
```
