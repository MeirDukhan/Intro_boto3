


import json
import boto3


#ec2 = boto3.resource('ec2', region_name='eu-west-1')
#client = boto3.client('ec2')

# Show available profiles in ~/.aws/credentials
print (boto3.session.Session().available_profiles)


# Change the profile of the default session in code
# Use profile 'meir3'
boto3.setup_default_session(profile_name='meir3')
s3meir3 = boto3.resource('s3')

print()

ec2 = boto3.resource('ec2', region_name='eu-west-1')

# create VPC
vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
# we can assign a name to vpc, or any resource, by using tag
vpc.create_tags(Tags=[{"Key": "Name", "Value": "boto3_vpc"}])
vpc.wait_until_available()
print(vpc.id)

# create then attach internet gateway
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)
