FROM python:3.11-slim

ARG USE_PROXY=false

RUN if [ "$USE_PROXY" = "true" ]; then \
        echo " Enabling proxy"; \
        export http_proxy="http://163.116.128.80:8080"; \
        export https_proxy="http://163.116.128.80:8080"; \
        ENV http_proxy="http://163.116.128.80:8080"; \
        ENV https_proxy="http://163.116.128.80:8080"; \
    else \
        echo " Proxy disabled"; \
    fi

WORKDIR /srv

COPY download_model/nemotron-speech-streaming/nemotron-speech-streaming-en-0.6b.nemo nemotron-speech-streaming-en-0.6b.nemo

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip setuptools wheel
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app app

COPY app/google_credentials.json google_credentials.json


ENV GOOGLE_APPLICATION_CREDENTIALS=/srv/google_credentials.json
ENV GOOGLE_RECOGNIZER=projects/eci-ugi-digital-ccaipoc/locations/us-central1/recognizers/google-stt-default
ENV GOOGLE_REGION=us-central1
ENV GOOGLE_LANGUAGE=en-US
ENV GOOGLE_MODEL=latest_short
ENV GOOGLE_INTERIM=true
ENV GOOGLE_EXPLICIT_DECODING=true

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]

for this getting this 
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/asr-realtime-custom-vad-download#  docker build --build-arg USE_PROXY=true -t cx_asr_realtime_custom_vad .
[+] Building 0.6s (7/14)                                                                                                                                                   docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                 0.0s
 => => transferring dockerfile: 1.19kB                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                  0.2s
 => [auth] library/python:pull token for registry-1.docker.io                                                                                                                        0.0s
 => [internal] load .dockerignore                                                                                                                                                    0.0s
 => => transferring context: 2B                                                                                                                                                      0.0s
 => CACHED [1/9] FROM docker.io/library/python:3.11-slim@sha256:d6e4d224f70f9e0172a06a3a2eba2f768eb146811a349278b38fff3a36463b47                                                     0.0s
 => [internal] load build context                                                                                                                                                    0.0s
 => => transferring context: 6.86kB                                                                                                                                                  0.0s
 => ERROR [2/9] RUN if [ "true" = "true" ]; then         echo " Enabling proxy";         export http_proxy="http://163.116.128.80:8080";         export https_proxy="http://163.116  0.3s
------
 > [2/9] RUN if [ "true" = "true" ]; then         echo " Enabling proxy";         export http_proxy="http://163.116.128.80:8080";         export https_proxy="http://163.116.128.80:8080";         ENV http_proxy="http://163.116.128.80:8080";         ENV https_proxy="http://163.116.128.80:8080";     else         echo " Proxy disabled";     fi:
0.205  Enabling proxy
0.206 /bin/sh: 1: ENV: not found
0.206 /bin/sh: 1: ENV: not found
------

 1 warning found (use docker --debug to expand):
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "GOOGLE_APPLICATION_CREDENTIALS") (line 29)
Dockerfile:5
--------------------
   4 |
   5 | >>> RUN if [ "$USE_PROXY" = "true" ]; then \
   6 | >>>         echo " Enabling proxy"; \
   7 | >>>         export http_proxy="http://163.116.128.80:8080"; \
   8 | >>>         export https_proxy="http://163.116.128.80:8080"; \
   9 | >>>         ENV http_proxy="http://163.116.128.80:8080"; \
  10 | >>>         ENV https_proxy="http://163.116.128.80:8080"; \
  11 | >>>     else \
  12 | >>>         echo " Proxy disabled"; \
  13 | >>>     fi
  14 |
--------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c if [ \"$USE_PROXY\" = \"true\" ]; then         echo \" Enabling proxy\";         export http_proxy=\"http://163.116.128.80:8080\";         export https_proxy=\"http://163.116.128.80:8080\";         ENV http_proxy=\"http://163.116.128.80:8080\";         ENV https_proxy=\"http://163.116.128.80:8080\";     else         echo \" Proxy disabled\";     fi" did not complete successfully: exit code: 127


