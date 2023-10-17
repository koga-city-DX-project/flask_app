FROM python:3.9

WORKDIR /usr/src
COPY /requirements.txt ./

# upgrade pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

