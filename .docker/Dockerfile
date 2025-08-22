FROM ubuntu:22.04

WORKDIR /code

RUN apt-get update && \
    # necessary packages
    apt-get install -y python3 python3-pip git postgresql-client openssh-client wait-for-it && \
    # debugging and utils packages
    apt-get install -y iputils-ping telnet netcat net-tools dnsutils curl wget procps less vim

COPY .docker/requirements.txt /code/

RUN pip install --upgrade pip && pip install -r /code/requirements.txt
