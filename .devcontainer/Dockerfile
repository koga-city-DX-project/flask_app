FROM python:3.9.18
WORKDIR /usr/src

USER root

RUN apt update
RUN apt install -y git
# upgrade pip
RUN pip install --upgrade pip
EXPOSE 5000
