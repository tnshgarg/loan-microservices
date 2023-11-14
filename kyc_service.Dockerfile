FROM python:3.10-alpine

# set working directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install os dependencies
RUN apk --no-cache add musl-dev linux-headers g++
RUN apk update && apk add --no-cache chromium chromium-chromedriver
RUN ln -s /usr/bin/chromium /usr/bin/google-chrome

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt
# add app
COPY . /usr/src/app

# run gunicorn
CMD uvicorn --host 0.0.0.0 --port 80 main:app