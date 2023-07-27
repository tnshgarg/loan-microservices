FROM python:3.10-alpine

# set working directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production
ENV APP_SETTINGS media_processing.config.ProductionConfig

# add and install requirements
COPY ./media_processing/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

# add app
COPY . /usr/src/app

# run gunicorn
CMD gunicorn --bind 0.0.0.0:80 manage:app