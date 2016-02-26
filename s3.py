#!/usr/bin/env python
import boto3

s3 = boto3.resource('s3')

bucket = s3.create_bucket(Bucket='cpug')
bucket.upload_file('image.png', 'image.png')


print(bucket.name + ' contents:')
for o in bucket.objects.all():
    print(o.key)
