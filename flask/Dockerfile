FROM python:latest
ARG DEBIAN_FRONTEND=noninteractive
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /usr/local/bin/app/
WORKDIR /usr/local/bin/app/
CMD guincorn -b 0.0.0.0:8000 app:app
