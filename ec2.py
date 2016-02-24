#!/usr/bin/env python
import boto3

ec2 = boto3.resource('ec2')

# launch an instance
instances = ec2.create_instances(ImageId='ami-11032472',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=1)
