FROM python:3.10-alpine

# set working directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# add and install requirements
COPY ./kyc_service/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

# add app
COPY . /usr/src/app

# run gunicorn
CMD uvicorn --host 0.0.0.0 --port 80 kyc_service.main:app