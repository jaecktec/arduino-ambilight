FROM    ubuntu:20.04
ENV TZ=Europe/Berlin
ARG DEBIAN_FRONTEND=noninteractive

RUN     apt update && apt upgrade -y
RUN     apt install -y autoconf automake libtool curl make g++ unzip build-essential mc vim git python3 python3-pip

RUN     git clone -b master --single-branch --depth 1 https://github.com/protocolbuffers/protobuf.git
WORKDIR protobuf
RUN     ./autogen.sh
RUN     ./configure
RUN     make -j 10
RUN     make install
RUN     ldconfig
WORKDIR python
RUN     python3 setup.py build
RUN     python3 setup.py test
RUN     python3 setup.py install

WORKDIR /
RUN     git clone -b master --single-branch --depth 1 https://github.com/nanopb/nanopb.git
WORKDIR /nanopb/generator/proto
RUN     make -j 10
RUN     echo "export PATH=$PATH:/nanopb/generator/">.bashrc
WORKDIR /workspace
