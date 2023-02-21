FROM python:3.10.4-alpine

WORKDIR /application

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev bash postgresql-client

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
