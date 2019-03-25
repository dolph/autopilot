FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y \
    chromium-chromedriver \
    python-pip \
    python2.7

COPY . /app
WORKDIR /app
RUN pip install .
CMD autopilot --help
