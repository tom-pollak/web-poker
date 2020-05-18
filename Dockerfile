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

CMD gunicorn project.asgi:application -k uvicorn.workers.UvicornWorker

