#!/usr/bin/env python

'''
Description:

Author:
Matthew Feng, mattfeng@mit.edu
'''

import argparse
import requests

# Location of the player repo server
PLAYER_REPO_SERVER = '34.233.102.237'

def check_unique_name(name):
    pass

def upload_player(path):
    pass

def add_player_to_db():
    requests.post(PLAYER_REPO_SERVER, )

def main():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('name',
        help = 'name of the bot (must be unique!)'
        )
    parser.add_argument()

    args = parser.parse_args()

    main()