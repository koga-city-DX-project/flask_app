FROM nvcr.io/nvidia/rapidsai/base:23.10-cuda12.0-py3.9

WORKDIR /usr/src

USER root

RUN apt update
RUN apt install -y git
# upgrade pip
RUN pip install --upgrade pip

