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
import json
import os

from botocore.exceptions import ClientError
from pyleiser.util import error, info

# Location of the player repo server
PLAYER_REPO_SERVER = 'http://34.233.102.237/'
CUSTOM_AWS_CREDS = json.load(open('creds.json'))
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
    resp = requests.post(PLAYER_REPO_SERVER + '/add', data = data)
    resp_json = json.loads(resp.text)
    if 'error' in resp_json:
        err = resp_json['error']
        error('Failed to add player `{}` to our custom database: {}'.format(name, err))
        exit(1)
    else:
        info(resp.text)

def check_player_in_db(name):
    resp = requests.post(PLAYER_REPO_SERVER + '/check', data = {'name': name})
    if resp.text == 'exists':
        error('A bot named `{}` already exists!'.format(name))
        exit(1)
    elif resp.text == 'bad request':
        error('A malformed request was made')
        exit(1)


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

def upload_binary_to_custom_s3_bucket(botname, filepath, zipfile, bucket):
    ''' Uploads a binary and source directory to a custom S3 bucket. '''
    s3_client = boto3.client('s3',
        **CUSTOM_AWS_CREDS
    )

    binary_obj = botname
    if zipfile is not None:
        zip_obj = '{}-src.zip'.format(botname)

    try:
        s3_client.upload_file(filepath, bucket, binary_obj)
        if zipfile is not None:
            s3_client.upload_file(zipfile, bucket, zip_obj)
    except ClientError as e:
        error('Uploading binary and source to custom S3 failed.')
        print(e)
        exit(1)
    
    if zipfile is not None:
        info('Uploaded source `{}` and binary `{}` successfully!'.format(zip_obj, binary_obj))
    else:
        info('Uploaded binary `{}` successfully!'.format(binary_obj))


def main(binary, srcpath, botname, botdesc):
    ALLOWED_CHARS = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    if not all(c in ALLOWED_CHARS for c in botname):
        error('Bot name must only contain alphanumeric characters or the underscore.')
        exit(1)

    if not os.path.isfile(binary):
        error('`{}` is not a file.'.format(binary))
        exit(1)
    
    if srcpath is not None and not os.path.isdir(srcpath):
        error('`{}` is not a directory.'.format(srcpath))
        exit(1)
    
    check_player_in_db(botname)

    if srcpath is None:
        info('No source directory has been provided. '
             'Are you sure you want to upload a binary '
             'without the corresponding source?')
        if input('(y / n)').lower() != 'y':
            info('User canceled upload operation.')
            exit(1)
        
    zip_path = None
    if srcpath is not None:
        zip_path = zip_source_code(srcpath)
        info('Zipped source code at `{}` to `{}`.'.format(srcpath, zip_path))

    athena_user, iam_user = get_user()
    official_name = '{}.{}'.format(athena_user, botname)

    info('Bot official_name is `{}`.'.format(official_name))

    # Upload binary to custom bucket
    upload_binary_to_custom_s3_bucket(botname, binary, zip_path, CUSTOM_S3_BUCKET)

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