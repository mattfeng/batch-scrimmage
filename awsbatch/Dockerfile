FROM ubuntu:xenial

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:wsmoses/tapir-toolchain
RUN apt-get update
RUN apt-get install -y tapirclang-5.0 libcilkrts5
RUN apt-get install -y wget unzip
RUN apt-get install -y build-essential clang
RUN apt-get install -y 
RUN apt-get install -y openjdk-8-jdk tcl

WORKDIR /

ENTRYPOINT []
