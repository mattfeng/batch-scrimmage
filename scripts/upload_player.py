#!/usr/bin/env python

'''
Description:
Uploads a player bot to the official scrimmage server,
the custom AWS autotester server, and to the database
to keep track of bots and bot changes.

Author:
Matthew Feng, mattfeng@mit.edu
'''

import argparse
import requests
import getpass
import boto3

from pyleiser.util import error, info

# Location of the player repo server
PLAYER_REPO_SERVER = 'http://34.233.102.237/add'

# Amazon S3 bucket name.
STUDENT_BUCKET = '6172-test-filesystem'

# Key prefix for user folders in bucket.
OBJECT_KEY_PREFIX = 'userhome'

# Key folder for bot binaries.
OBJECT_KEY_BINARIES = 'autotest_binary_uploads'

# Server for registering binaries.
REG_SERVER = 'cloud9.csail.mit.edu:4040'

def check_unique_name(name):
    pass

def upload_player(path):
    pass

def add_player_to_db(name, official_name, desc):
    data = {
        'name': name,
        'official_name': official_name,
        'desc': desc
    }
    resp = requests.post(PLAYER_REPO_SERVER, data = data)
    print(resp.text)

def get_user():
    try:
        athena_user = str(getpass.getuser())
        iam_user = 'student-{}'.format(athena_user)
    except Exception as e:
        error('Could not get student username.')
        print(e)
        exit(1)
    
    info('Found username `{}`, IAM user `{}`.'.format(athena_user, iam_user))
    
    return athena_user, iam_user

def test_s3_bucket_valid():
    # Test for bucket existence.
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(STUDENT_BUCKET)

    try:
        s3.meta.client.head_bucket(Bucket = STUDENT_BUCKET)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response["Error"]["Code"])

        if error_code == 404:
            error('Amazon S3 Bucket `{}` does not exist.'.format(STUDENT_BUCKET))
        else:
            error('Could not get Amazon S3 bucket.')
            print(e)
            exit(1)
    
    info('Using bucket `{}`.'.format(STUDENT_BUCKET))
    
    return s3, bucket

def upload_binary_to_s3_bucket(botname, binary, iam_user, athena_user):
    ''' Uploads a binary to the student bucket. '''

    s3_client = boto3.client('s3')
    upload_key = '/'.join([
        OBJECT_KEY_PREFIX,
        iam_user,
        OBJECT_KEY_BINARIES,
        botname
    ])

    info('Uploading bot `{}` located at path '
         '`{}` to ~/s3home/{}/{} on instance.'.format(
            botname,
            binary,
            OBJECT_KEY_BINARIES,
            botname,
            )
        )

    try:
        s3_client.upload_file(
            binary,
            STUDENT_BUCKET,
            upload_key,
            ExtraArgs={
                'ACL': 'bucket-owner-full-control'
            }
        )
    except Exception as e:
        error('Was not able to upload bot to the Amazon S3 bucket.')
        print(e)
        exit(1)

    # Register the binary with the server.
    info('Registering bot `{}` with server...'.format(botname))

    endpoint = 'http://{}/upload/{}/{}'.format(REG_SERVER, botname, athena_user)
    try:
        resp = requests.get(endpoint)
    except Exception as e:
        error('Cannot contact registration server `{}`.'.format(REG_SERVER))
        print(e)
        exit(1)

    if len(resp.text) > 0:
        error('Server error: {}'.format(resp.text))
        exit(1)
    else:
        info('Registration success!')


def main(binary, botname, botdesc):
    athena_user, iam_user = get_user()
    official_name = '{}.{}'.format(athena_user, botname)

    info('Bot official_name is `{}`.'.format(official_name))

    # Fetch the bucket.
    s3, bucket = test_s3_bucket_valid()
    
    upload_binary_to_s3_bucket(botname, binary, iam_user, athena_user)
    add_player_to_db(botname, official_name, botdesc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('binary',
        help = 'path to binary of leiserchess client',
        type = str
        )

    parser.add_argument('botname',
        help = 'name of the bot (must be unique!)',
        type = str
        )

    parser.add_argument('botdesc',
        help = 'description of the bot (e.g. changes that were made)',
        type = str
        )

    args = parser.parse_args()

    main(
        binary  = args.binary,
        botname = args.botname,
        botdesc = args.botdesc
        )