#!/bin/bash


cd /
wget https://leiserchess.s3.amazonaws.com/leiserchess_autotester.zip
unzip leiserchess_autotester.zip

cd leiserchess_autotester
cd BayesElo
make
cd ../autotester
make
cd ../tests

# get the test specification
echo ${TEST_SPECIFICATION} >> autotest.txt

java -jar lauto.jar autotest.txt
