FROM openwhisk/python3action

COPY lookbusy-1.4.tar.gz .
RUN tar -xvf lookbusy-1.4.tar.gz
RUN apk add build-base

RUN  cd ./lookbusy-1.4 && ./configure && make && make install
