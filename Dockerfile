FROM python:3.9

WORKDIR /usr/src/app
ENV FLASK_APP=app
COPY /app/requirements.txt ./

# upgrade pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

