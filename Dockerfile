FROM python

ADD . /root/testblame/
WORKDIR /root/testblame/

RUN sh setup.sh 

ENTRYPOINT testblame

