FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

ARG PORT
CMD python manage.py cleartables
CMD python manage.py collectstatic
CMD daphne project.asgi:application --port $PORT --bind 0.0.0.0 
