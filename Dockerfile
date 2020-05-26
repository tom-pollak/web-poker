FROM python:3.7

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

ARG PORT
#CMD python manage.py runserver 0.0.0.0:80
#CMD gunicorn project.asgi:application -k uvicorn.workers.UvicornWorker
CMD daphne project.asgi:application --port $PORT --bind 0.0.0.0 
