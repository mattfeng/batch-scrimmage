FROM continuumio/miniconda3

# move to a unified location
RUN mkdir /player-repo-server
WORKDIR /player-repo-server

# set up requirements
COPY requirements.txt .
RUN conda create -y -n server python=3.7
RUN pip install -r requirements.txt

# copy secret
COPY aws.secret .
