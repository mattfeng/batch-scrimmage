#!/bin/bash

pip install boto3
pip install requests

cd /leiserchess
wget https://leiserchess.s3.amazonaws.com/leiserchess_autotester-log.zip
unzip leiserchess_autotester-log.zip

cd leiserchess_autotester-log
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

echo -e '\n'
echo 'Downloading players...'
/leiserchess/download_players.py autotest.txt

java -jar lauto.jar autotest.txt

# get scrimmage UUID
SCRIM_UUID=$2

zip games_${SCRIM_UUID}.zip *.log autotest.pgn autotest.txt

ls
