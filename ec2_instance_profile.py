#!/usr/bin/env python
import boto3
import botocore.exceptions


# delegate access to EC2
delegate = """{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "ec2.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"""

iam = boto3.resource('iam')

# create role, delegated to EC2
try:
    iam.create_role(RoleName='s3_access_role', AssumeRolePolicyDocument=delegate)
except botocore.exceptions.ClientError:
    pass

# give access to cpug bucket
policy_doc = """{
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::cpug/*"
    ]
  }
}
"""

# create policy to give access to S3
try:
    policy = iam.create_policy(PolicyName='s3_access_policy', PolicyDocument=policy_doc)
    policy.attach_role(RoleName='s3_access_role')
except botocore.exceptions.ClientError:
    pass

# create instance profile, which uses the role, which has the policy attached
try:
    instance_profile = iam.create_instance_profile(InstanceProfileName='s3_access_profile')
    instance_profile.add_role(RoleName='s3_access_role')
except botocore.exceptions.ClientError:
    pass


ec2 = boto3.resource('ec2')

# allow HTTP access
try:
    security_group = ec2.create_security_group(GroupName='http_access',
                                               Description='pug talk')
    security_group.authorize_ingress(IpProtocol='tcp',
                                     CidrIp='0.0.0.0/0',
                                     FromPort=80,
                                     ToPort=80)
except botocore.exceptions.ClientError:
    pass

# download from s3, put it on web server
user_data = """#!/bin/bash
# install web server
yum install httpd -y
aws s3 cp s3://cpug/image.png /var/www/icons/image.png
echo "<img src='../icons/image.png'>" > /var/www/html/index.html
service httpd start"""

instances = ec2.create_instances(ImageId='ami-11032472',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=1,
                                 KeyName='cpug',
                                 SecurityGroupIds=['http_access'],
                                 UserData=user_data,
                                 IamInstanceProfile={'Name': 's3_access_profile'})


print('launching')

instances[0].wait_until_running()
print('running (and installing web server)')
ip_address = ec2.Instance(instances[0].id).public_ip_address

import time
import socket

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip_address, 80))
        break
    except:
        pass

    s.close()
    time.sleep(1)

print('type: open http://' + ip_address)
