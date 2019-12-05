#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Description:
Uploads a player bot to the official scrimmage server,
the custom AWS autotester server, and to the database
to keep track of bots and bot changes.

Author:
Matthew Feng, mattfeng@mit.edu
'''

import shutil
import argparse
import requests
import getpass
import boto3
import uuid

from pyleiser.util import error, info

# Location of the player repo server
PLAYER_REPO_SERVER = 'http://34.233.102.237/add'
CUSTOM_S3_BUCKET = 'leiserchess'

# Amazon S3 bucket name.
STUDENT_BUCKET = '6172-test-filesystem'

# Key prefix for user folders in bucket.
OBJECT_KEY_PREFIX = 'userhome'

# Key folder for bot binaries.
OBJECT_KEY_BINARIES = 'autotest_binary_uploads'

# Server for registering binaries.
REG_SERVER = 'cloud9.csail.mit.edu:4040'

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

def test_6172_s3_bucket_valid():
    # Test for bucket existence.
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(STUDENT_BUCKET)

    try:
        s3.meta.client.head_bucket(Bucket = STUDENT_BUCKET)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])

        if error_code == 404:
            error('Amazon S3 Bucket `{}` does not exist.'.format(STUDENT_BUCKET))
        else:
            error('Could not get Amazon S3 bucket.')
            print(e)
            exit(1)
    
    info('Using bucket `{}`.'.format(STUDENT_BUCKET))

def upload_binary_to_6172_s3_bucket(botname, binary, iam_user, athena_user):
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

def zip_source_code(srcpath):
    file_uuid = uuid.uuid4()
    fname = '/tmp/leiserchess_{}'.format(file_uuid)
    shutil.make_archive(fname, 'zip', srcpath)
    return fname + '.zip'

def upload_binary_to_custom_s3_bucket():
    ''' Uploads a binary and source directory to a custom S3 bucket. '''
    s3_client = boto3.client('s3')

def main(binary, srcpath, botname, botdesc):
    ALLOWED_CHARS = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    if not all(c in ALLOWED_CHARS for c in botname):
        error('Bot name must only contain alphanumeric characters or the underscore.')
        exit(1)

    if srcpath is None:
        info('No source directory has been provided. '
             'Are you sure you want to upload a binary '
             'without the corresponding source?')
        if input('(y / n)').lower() != 'y':
            info('User canceled upload operation.')
            exit(1)
        
    if srcpath is not None:
        zip_path = zip_source_code(srcpath)
        info('Zipped source code at `{}` to `{}`.'.format(srcpath, zip_path))
        # upload_src_to_custom_s3_bucket(botname, binary)

    quit()

    athena_user, iam_user = get_user()
    official_name = '{}.{}'.format(athena_user, botname)

    info('Bot official_name is `{}`.'.format(official_name))

    # Fetch the bucket.
    
    # Upload binary to custom bucket
    upload_binary_to_custom_s3_bucket(botname, binary, iam_user)

    # Upload binary to 6.172 S3 bucket
    #test_6172_s3_bucket_valid()
    #upload_binary_to_6172_s3_bucket(botname, binary, iam_user, athena_user)

    # Register bot with custom database
    add_player_to_db(botname, official_name, botdesc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('binary',
        help = 'path to binary of leiserchess client',
        type = str
        )

    parser.add_argument('-s', '--src',
        help = 'path to folder with the source files',
        type = str,
        default = None,
        dest = 'srcpath'
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
        srcpath = args.srcpath,
        botname = args.botname,
        botdesc = args.botdesc
        )