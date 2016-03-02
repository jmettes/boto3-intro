#!/usr/bin/env python

from troposphere import Template, Ref, Base64
import troposphere.ec2 as ec2
from troposphere.iam import Role, InstanceProfile, Policy as IAMPolicy
from awacs.aws import Allow, Statement, Principal, Policy, Action
from awacs.sts import AssumeRole
import boto3

template = Template()

http_sg = template.add_resource(ec2.SecurityGroup(
    "HTTPSecurityGroup",
    GroupDescription="Enable HTTP access via port 80",
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="80",
            ToPort="80",
            CidrIp="0.0.0.0/0",
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp="0.0.0.0/0",
        ),
    ],
))

role = template.add_resource(Role(
    "PugRole",
    AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[AssumeRole],
                Principal=Principal("Service", ["ec2.amazonaws.com"])
            )
        ]),
    Path="/",
    Policies=[IAMPolicy(
        "PugPolicy",
        PolicyName="PugPolicy",
        PolicyDocument=Policy(
            Statement=[
                Statement(Effect=Allow, Action=[Action("s3", "*")],
                          Resource=["arn:aws:s3:::cpug/*"])
            ]
        ))]))

instance_profile = template.add_resource(InstanceProfile(
    "PugInstanceProfile",
    Path="/",
    Roles=[{"Ref": "PugRole"}]
))

user_data = """#!/bin/bash
# install web server
yum install httpd -y
aws s3 cp s3://cpug/image.png /var/www/icons/image.png
echo "<img src='../icons/image.png'>" > /var/www/html/index.html
service httpd start"""

ec2_instance = template.add_resource(ec2.Instance(
    "Ec2Instance",
    ImageId="ami-11032472",
    InstanceType="t2.micro",
    KeyName="cpug",
    SecurityGroups=[Ref(http_sg)],
    UserData=Base64(user_data),
    IamInstanceProfile=Ref(instance_profile)
))


cloudformation = boto3.resource('cloudformation')
cloudformation.create_stack(StackName='pug',
                            TemplateBody=template.to_json(),
                            Capabilities=['CAPABILITY_IAM'])
