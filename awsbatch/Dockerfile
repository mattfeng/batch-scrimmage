FROM ubuntu:xenial

# install dependencies
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:wsmoses/tapir-toolchain
RUN apt-get update
RUN apt-get install -y tapirclang-5.0 libcilkrts5
RUN apt-get install -y wget unzip
RUN apt-get install -y build-essential clang
RUN apt-get install -y 
RUN apt-get install -y openjdk-8-jdk tcl

# get Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /install_miniconda.sh
RUN bash /install_miniconda.sh -b -p /miniconda3
RUN eval "$(/miniconda3/bin/conda shell.bash hook)"

# move to the correct directory and start the build and test script
RUN mkdir /leiserchess
WORKDIR /leiserchess

COPY run_autotest.sh .
RUN chmod +x run_autotest.sh
COPY upload_to_s3.py .
RUN chmod +x upload_to_s3.py
COPY download_players.py .
RUN chmod +x download_players.py

RUN echo "source activate base" > ~/.bashrc
ENV PATH /miniconda3/bin:$PATH

ENTRYPOINT ["/leiserchess/run_autotest.sh"]
CMD []
