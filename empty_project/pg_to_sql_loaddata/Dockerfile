FROM python:3.10

WORKDIR /opt/app
COPY . .
RUN chmod 777 /opt/app/entrypoint.sh.sh

RUN apt -y update \
    && apt -y install netcat

RUN pip install --upgrade pip \
     && pip install -r req.txt

ENTRYPOINT ["/opt/app/entrypoint.sh"]