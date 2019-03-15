

'''
boto3 sample and simple creation of resources in an AWS region. 
Learning purpose.

	Create key pair and save it on disk 
	Create VPC
	Create then attach internet gateway
	create a route table and a public route
	create subnet 
	Create sec group
	Create an instance

''' 


import os
import json
import boto3
import requests 


# Sources & Credits: 
#	https://gist.github.com/nguyendv/8cfd92fc8ed32ebb78e366f44c2daea6
# 	https://sdbrett.com/BrettsITBlog/2016/05/creating-aws-instances-with-boto3/
#   boto3 documentation 
# 

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

# Delete key pair on AWS region 
ec2_client = boto3.client('ec2', region_name='eu-west-1')
response = ec2_client.delete_key_pair(KeyName='boto3_kp')

# Delete key pair from disk, if exists
key_pair_fname = '/Users/meirdu/.ssh/boto3_kp.pem'
if os.path.exists(key_pair_fname): 
	print('Deleting key pair: {}'.format(key_pair_fname))
	os.remove(key_pair_fname)

# Create key pair and save it on disk with 0400 permissions
outfile = open(key_pair_fname,'w')
key_pair = ec2.create_key_pair(KeyName='boto3_kp')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
outfile.close()
os.chmod(outfile.name, 0o400)


# create VPC
vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
# we can assign a name to vpc, or any resource, by using tag
vpc.create_tags(Tags=[{"Key": "Name", "Value": "boto3_vpc"}])
vpc.wait_until_available()
print(vpc.id)

# Create internet gateway
ig = ec2.create_internet_gateway()

# To attach VPC to IGW, we can either via a vpc method or an igw method (in comment thereafter)
# vpc.attach_internet_gateway(InternetGatewayId=ig.id)

# Or, attach IGW to VPC
ig.attach_to_vpc(VpcId=vpc.id)
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

# Get our public IP so we'll allow SSH connections only from it
r = requests.get('http://ipinfo.io/ip')
my_ip = r.text.strip()


# Create sec group
# First, build the CIDR we want to allow SSH from 
CidrIp_Allowed = my_ip + '/32' 

sec_group = ec2.create_security_group(
    GroupName='boto3_SG', Description='boto3_SG sec group', VpcId=vpc.id)
sec_group.authorize_ingress(
    CidrIp=CidrIp_Allowed,
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

# To get the Public IP address, we need to access the ec2 instance at the boto3 'resource' level 
# and (not at 'client' as our just created instance)
# For a detailed desription of the ec2 instance at 'resource' level, see:
# 		https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Instance.wait_until_running 
# 
# Wait a little bit before trying to get the public IP address.
# TO Check: Why call to wait_until_running() does not to the trick)

print('Waiting 40 seconds -- to get the public IP')
import time 
time.sleep(40)

ec2_resource = boto3.resource('ec2', region_name='eu-west-1')
instance_resource = ec2_resource.Instance(instances[0].id)

print(instance_resource.public_dns_name)

