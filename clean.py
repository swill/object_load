#!/usr/bin/env python

import boto
import boto.s3.connection
import swiftclient
import os
import time

# package specific imports
from config import *

def all_files(directory):
    for path, dirs, files in os.walk(directory):
        for f in files:
            yield os.path.join(path, f)
            
def s3_api(provider, connection, bucket_name='global_unique_bucket_name'):
    # create connection
    conn = boto.connect_s3(
        host = connection['host'],
        aws_access_key_id = connection['access_key'],
        aws_secret_access_key = connection['secret_key'],
        calling_format = boto.s3.connection.OrdinaryCallingFormat()
    )
    
    try:
        # get the bucket
        bucket = conn.get_bucket(bucket_name)
    
        # remove the objects from the bucket
        for obj in bucket.list():
            bucket.delete_key(obj.name)

        # remove the bucket we created at the beginning of the script
        conn.delete_bucket(bucket.name)

        print "cleaned: "+provider+" using the s3 api has finished..."
    except:
        print provider+" does not need to be cleaned..."
                
                
def swift_api(provider, connection, bucket_name='global_unique_bucket_name'):
    conn = swiftclient.client.Connection(**connection)
    try:
        # remove the objects from the bucket
        for obj in conn.get_container(bucket_name)[1]:
            conn.delete_object(bucket_name, obj['name'])

        # remove the bucket we created at the beginning of the script
        conn.delete_container(bucket_name)
    
        print "cleaned: "+provider+" using the swift api has finished..."
    except:
        print provider+" does not need to be cleaned..."
    

if __name__ == "__main__":
    # clean the test cases
    for test_case in test_cases:
        for api in test_case['apis']:
            if test_case['provider'] in connections and api in connections[test_case['provider']]:
                connection = connections[test_case['provider']][api]
                if api == 's3':
                    s3_api(test_case['provider'], connection, unique_container_name)
                if api == 'swift':
                    swift_api(test_case['provider'], connection, unique_container_name)
        
    
    
