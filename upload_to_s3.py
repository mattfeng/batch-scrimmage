#!/usr/bin/env python

import boto3
import argparse

from botocore.exceptions import ClientError

def main(file_name, bucket):
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(file_name, bucket)
    except ClientError as e:
        print('Was not able to upload file `{}`'.format(file_name)
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument()
    parser.add_argument('-b', '--bucket',
        help = 'name of AWS S3 bucket to upload to',
        type = str,
        default = ''
        )

    args = parser.parse_args()

    main()
