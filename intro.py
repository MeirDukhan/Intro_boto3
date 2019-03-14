


import json
import boto3


#ec2 = boto3.resource('ec2', region_name='eu-west-1')
#client = boto3.client('ec2')

# Show available profiles in ~/.aws/credentials
print (boto3.session.Session().available_profiles)

# Show buckets in the 'default' profile 
s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
    print("NMI: " + bucket.name)

# Change the profile of the default session in code
# Use profile 'meir3'
boto3.setup_default_session(profile_name='meir3')
s3meir3 = boto3.resource('s3')

print()
for bucket in s3meir3.buckets.all():
    print('Personal buckets: ' + bucket.name )

boto3.setup_default_session(profile_name='meir')
s3meir = boto3.resource('s3')
print()
for bucket in s3meir.buckets.all():
	print('buckets of "meir" profile: ' + bucket.name )

print('\n\n')
for prof in boto3.session.Session().available_profiles: 
	boto3.setup_default_session(profile_name=prof)
	s3prof = boto3.resource('s3')
	print()
	for bucket in s3prof.buckets.all(): 
		print('buckets of profile {}: {}'.format(prof, bucket.name))

