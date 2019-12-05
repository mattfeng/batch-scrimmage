#!/usr/bin/env python

'''
Description:
This program parses a ATFile and downloads the appropriate
binaries from the custom S3 repository.

Author:
Matthew Feng, mattfeng@mit.edu
'''

import argparse
import requests
import os
import stat

S3_REPO_BASE = 'https://leiserchess.s3.amazonaws.com'

def parse_at_file(fpath):
    ''' Finds all the players in an ATFile. '''
    
    players = []

    with open(fpath) as f:
        for line in f:
            line = line.strip()
            if line.startswith('player'):
                _, name = line.split('=')
                name = os.path.basename(name.strip())
                players.append(name)

    return players
    

def main(at_file):
    players = parse_at_file(at_file)

    for player in players:
        print('Found player: {}'.format(player))

    for player in players:
        target = '{}/{}'.format(S3_REPO_BASE, player)
        print('Downloading player from {}'.format(target))
        r = requests.get(target, allow_redirects = True)

        if 'AccessDenied' in r.text:
            print('ERROR: player `{}` was not found.'.format(player))
            print(r.text)
            quit()
        else:
            open(player, 'wb').write(r.content)
            os.chmod(player, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('atfile',
        help = 'file containing the tournament format',
        type = str
        )

    args = parser.parse_args()

    main(args.atfile)

