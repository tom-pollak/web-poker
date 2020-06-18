# web_poker
## poker web-app written in django

Check out the website here: [pollakpoker.live](https://www.pollakpoker.live)

Prerequisites: Docker, Docker Compose

to run locally:
```
echo "PORT=8000" > .env
echo "POSTGRES_HOST_AUTH_METHOD=trust" > .env #### ONLY for running locally
docker-compose exec web python manage.py migrate
docker-compose up --build -d
```
