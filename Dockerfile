FROM nvcr.io/nvidia/rapidsai/base:23.10-cuda12.0-py3.9

WORKDIR /usr/src
COPY /requirements.txt ./

USER root

RUN apt update
RUN apt install -y git
# upgrade pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir data
RUN mkdir data/save
