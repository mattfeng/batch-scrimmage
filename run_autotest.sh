#!/bin/bash

echo $(which conda)
conda init bash
conda activate base
pip install boto3
pip install requests

cd /leiserchess
wget https://leiserchess.s3.amazonaws.com/leiserchess_autotester.zip
unzip leiserchess_autotester.zip

cd leiserchess_autotester
cd BayesElo
make
cd ../autotester
make
cd ../tests

# get the test specification
TEST_SPEC_URL=$1
echo "TEST_SPEC_URL = $TEST_SPEC_URL"
wget $TEST_SPEC_URL -O autotest.txt

echo 'Running autotests with the following ATFile:'
cat autotest.txt

echo '\n'
echo 'Downloading players...'
/leiserchess/download_players.py autotest.txt

java -jar lauto.jar autotest.txt
