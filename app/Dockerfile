FROM ubuntu

RUN apt-get update

RUN apt-get install -y python3 python3-pip

ADD . ./

RUN pip install -r requirements.txt

CMD gunicorn -b 0.0.0.0:8050 main:server