#!/usr/bin/env python
import boto3
import botocore.exceptions

ec2 = boto3.resource('ec2')

# allow SSH access
try:
    security_group = ec2.create_security_group(GroupName='ssh_access',
                                               Description='pug talk')
    security_group.authorize_ingress(IpProtocol='tcp',
                                     CidrIp='0.0.0.0/0',
                                     FromPort=22,
                                     ToPort=22)
except botocore.exceptions.ClientError:
    pass


# create SSH key
try:
    key = ec2.create_key_pair(KeyName='cpug')
    with open('cpug.pem', 'w') as file:
        file.write(key.key_material)
except botocore.exceptions.ClientError:
    pass


# launch an instance with SSH key + Security Group (port 22)
instances = ec2.create_instances(ImageId='ami-11032472',
                                 InstanceType='t2.micro',
                                 MinCount=1,
                                 MaxCount=1,
                                 SecurityGroupIds=['ssh_access'],  # <-- security group
                                 KeyName='cpug')                   # <-- ssh key


print('launching')

instances[0].wait_until_running()
print('running')
ip_address = ec2.Instance(instances[0].id).public_ip_address

import time
import socket

print('running')
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip_address, 22))
        break
    except:
        pass

    s.close()
    time.sleep(1)

print('might need to run: chmod 400 cpug.pem')
print('type: ssh -i cpug.pem ec2-user@' + ip_address)
