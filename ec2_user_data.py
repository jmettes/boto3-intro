#!/usr/bin/env python
import boto3
import botocore.exceptions

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


# user-data script to install web server
user_data="""#!/bin/bash
# install web server
yum install httpd -y
echo "hello world!" > /var/www/html/index.html
service httpd start
"""

# launch an instance with
instances = ec2.create_instances(ImageId='ami-11032472',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=1,
                                 SecurityGroupIds=['http_access'],
                                 UserData=user_data)


print('launching')

instances[0].wait_until_running()
print('running')
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

print('running (and installing web server)')
print('type: open http://' + ip_address)
