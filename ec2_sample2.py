

import os
import json
import boto3

# Source https://gist.github.com/nguyendv/8cfd92fc8ed32ebb78e366f44c2daea6


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

# Delete key pair
ec2_client = boto3.client('ec2', region_name='eu-west-1')
response = ec2_client.delete_key_pair(KeyName='boto3_kp')

# Create key pair and save it on disk with 0400 permissions
outfile = open('~/.ssh/boto3_kp.pem','w')
key_pair = ec2.create_key_pair(KeyName='boto3_kp')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
outfile.close()
os.chmod('~/.ssh/boto3_kp.pem', 0o400)


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


# create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id
)
print(route_table.id)

# create subnet
subnet = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)
print(subnet.id)

# associate the route table with the subnet
route_table.associate_with_subnet(SubnetId=subnet.id)

# Create sec group
sec_group = ec2.create_security_group(
    GroupName='slice_0', Description='slice_0 sec group', VpcId=vpc.id)
sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)
print(sec_group.id)

# find image id ami-07683a44e80cd32c5 / eu-west-1
# Create instance
instances = ec2.create_instances(
    ImageId='ami-07683a44e80cd32c5', InstanceType='t2.micro', MaxCount=1, MinCount=1,
    NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}], 
    KeyName=key_pair.name)

instances[0].wait_until_running()
print(instances[0].id)

