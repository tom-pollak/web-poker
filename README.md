# web_poker
## poker web-app written in django

Check out the website here: [pollakpoker.live](https://www.pollakpoker.live)

Prerequisites: Docker, Docker Compose

to run locally:
```
docker-compose exec db psql -U postgres
```
inside db shell:
```
create database webpoker;
\q
```
then
```
docker-compose exec web python manage.py migrate
docker-compose up --build

```
