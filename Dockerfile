FROM python:3.7

ARG PASS

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

#CMD python manage.py runserver 0.0.0.0:80
CMD daphne project.asgi:application --port 80 --bind 0.0.0.0 -v2
#CMD gunicorn project.asgi:application -k uvicorn.workers.UvicornWorker

