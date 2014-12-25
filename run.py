#!/usr/bin/env python

import boto
import boto.s3.connection
import swiftclient
import os
import re
import shutil
import sys
import time

# package specific imports
from config import *

def all_files(directory):
    for path, dirs, files in os.walk(directory):
        for f in files:
            yield os.path.join(path, f)

def file_content(path):
    with open(path) as f:
        return f.read()
            
def s3_api(provider, connection, directories, test_cases, bucket_name='global_unique_bucket_name', clean_downloads=True):
    for test_case in test_cases:
        for i in range(test_case['batch_size']):
            # True, force downloads to run.  False, downloads run only if the downloads directory is empty.
            if (clean_downloads):
                # remove the downloads directory and recreate it to make sure we start from scratch
                if os.path.exists(directories['downloads']):
                    shutil.rmtree(directories['downloads'])
                os.makedirs(directories['downloads'])
                
            uploads_path = directories['uploads']+"/"+test_case['directory']+"/"
            downloads_path = directories['downloads']+"/"+provider+"/s3/"+test_case['directory']+"/"
            time_array = []

            with open(directories['logs']+'/'+provider+'_s3_'+test_case['directory']+'.log', 'a') as time_log:
                # identify the use case we are testing
                time_log.write(":using the s3 api on "+provider+" for directory "+uploads_path+"\n")
                args = {
                    'host':connection['host'], 
                    'aws_access_key_id':connection['access_key'],
                    'aws_secret_access_key':connection['secret_key'],
                    'is_secure':False,
                    'calling_format':boto.s3.connection.OrdinaryCallingFormat()
                }
                if 'port' in connection:
                    args['port'] = connection['port']
                if 'is_secure' in connection:
                    args['is_secure'] = connection['is_secure']
        
                # create connection
                start = time.time()
                conn = boto.connect_s3(**args)
                total = time.time()-start
                time_array.append(total)
                time_log.write("{0:.4f}".format(total).ljust(12)+":create connection\n")
            
                # create a bucket
                start = time.time()
                bucket = conn.create_bucket(bucket_name)
                total = time.time()-start
                time_array.append(total)
                time_log.write("{0:.4f}".format(total).ljust(12)+":create bucket\n")
    
                # upload objects to the new bucket
                for f in all_files(uploads_path):
                    try:
                        start = time.time()
                        obj = bucket.new_key(f[len(uploads_path):])
                        obj.set_contents_from_filename(f)
                        total = time.time()-start
                        time_array.append(total)
                        time_log.write("{0:.4f}".format(total).ljust(12)+str(obj.size).ljust(12)+":uploading object - "+obj.name+"\n")
                        file_size = os.path.getsize(f)
                        if obj.size != file_size:
                            with open(directories['logs']+'/errors.log', 'a') as error_log:
                                error_log.write(provider+" | s3 error on run "+str(i+1)+", '"+f+"' has a size of "+file_size+" but saved as "+obj.size+"\n")
                    except:
                        with open(directories['logs']+'/errors.log', 'a') as error_log:
                            error_log.write(provider+" | s3 error on run "+str(i+1)+" while uploading object: "+f+" -> "+repr(sys.exc_info()[1])+"\n")
                
                # download objects from the bucket
                for obj in bucket.list():
                    obj_path = str(obj.key)
                    full_path = downloads_path+obj_path
                    if not os.path.exists("/".join(full_path.split("/")[:-1])): # mkdir if it doesn't exist yet.
                        os.makedirs("/".join(full_path.split("/")[:-1]))
                    if not os.path.exists(full_path):
                        try:
                            start = time.time()
                            obj.get_contents_to_filename(full_path)
                            total = time.time()-start
                            time_array.append(total)
                            time_log.write("{0:.4f}".format(total).ljust(12)+str(obj.size).ljust(12)+":downloading object - "+obj.name+"\n")
                            file_size = os.path.getsize(full_path)
                            if obj.size != file_size:
                                with open(directories['logs']+'/errors.log', 'a') as error_log:
                                    error_log.write(provider+" | s3 error on run "+str(i+1)+", '"+full_path+"' has a size of "+file_size+", expected "+obj.size+"\n")
                        except:
                            with open(directories['logs']+'/errors.log', 'a') as error_log:
                                error_log.write(provider+" | s3 error on run "+str(i+1)+" while downloading object: "+full_path+" -> "+repr(sys.exc_info()[1])+"\n")
                
                # remove the objects from the bucket
                for obj in bucket.list():
                    try:
                        start = time.time()
                        bucket.delete_key(obj.name)
                        total = time.time()-start
                        time_array.append(total)
                        time_log.write("{0:.4f}".format(total).ljust(12)+str(obj.size).ljust(12)+":deleting object - "+obj.name+"\n")
                    except:
                        with open(directories['logs']+'/errors.log', 'a') as error_log:
                            error_log.write(provider+" | s3 error on run "+str(i+1)+" while deleting object: "+obj.name+" -> "+repr(sys.exc_info()[1])+"\n")
    
                # remove the bucket we created at the beginning of the script
                start = time.time()
                conn.delete_bucket(bucket.name)
                total = time.time()-start
                time_log.write("{0:.4f}".format(total).ljust(12)+":delete bucket\n")
                    
                total_time = sum(time_array)
                time_log.write("----------\n")
                time_log.write("{0:.4f}".format(total_time).ljust(12)+":total time for operations\n")
        
                time_log.write("\n\n")
        
                print provider+" using the s3 api on "+uploads_path+" run "+str(i+1)+" has finished..."
            # clean up the downloads directory if 'clean_downloads'
            if (clean_downloads):
                # remove the downloads directory and recreate it to make sure we start from scratch
                if os.path.exists(directories['downloads']):
                    shutil.rmtree(directories['downloads'])
                os.makedirs(directories['downloads'])
                
                
def swift_api(provider, connection, directories, test_cases, bucket_name='global_unique_bucket_name', clean_downloads=True):
    for test_case in test_cases:
        for i in range(test_case['batch_size']):
            # True, force downloads to run.  False, downloads run only if the downloads directory is empty.
            if (clean_downloads):
                # remove the downloads directory and recreate it to make sure we start from scratch
                if os.path.exists(directories['downloads']):
                    shutil.rmtree(directories['downloads'])
                os.makedirs(directories['downloads'])
                
            uploads_path = directories['uploads']+"/"+test_case['directory']+"/"
            downloads_path = directories['downloads']+"/"+provider+"/swift/"+test_case['directory']+"/"
            time_array = []

            with open(directories['logs']+'/'+provider+'_swift_'+test_case['directory']+'.log', 'a') as time_log:
                # identify the use case we are testing
                time_log.write(":using the swift api on "+provider+" for directory "+uploads_path+"\n")
        
                # create connection
                start = time.time()
                conn = swiftclient.client.Connection(
                    authurl=connection['auth_url'],
                    user=connection['username'],
                    key=connection['api_key']
                )
                total = time.time()-start
                time_array.append(total)
                time_log.write("{0:.4f}".format(total).ljust(12)+":create connection\n")
            
                # create a bucket
                start = time.time()
                conn.put_container(bucket_name)
                total = time.time()-start
                time_array.append(total)
                time_log.write("{0:.4f}".format(total).ljust(12)+":create container\n")
    
                # upload objects to the new bucket
                for f in all_files(uploads_path):
                    try:
                        content = file_content(f)
                        start = time.time()
                        conn.put_object(bucket_name, f[len(uploads_path):], content)
                        total = time.time()-start
                        time_array.append(total)
                        obj_head = conn.head_object(bucket_name, f[len(uploads_path):])
                        time_log.write("{0:.4f}".format(total).ljust(12)+obj_head['content-length'].ljust(12)+":uploading object - "+f[len(uploads_path):]+"\n")
                        if int(obj_head['content-length']) != len(content):
                            with open(directories['logs']+'/errors.log', 'a') as error_log:
                                error_log.write(provider+" | swift error on run "+str(i+1)+", '"+f+"' has a length of "+len(content)+" but saved as "+obj_head['content-length']+"\n")
                    except:
                        with open(directories['logs']+'/errors.log', 'a') as error_log:
                            error_log.write(provider+" | swift error on run "+str(i+1)+" while uploading object: "+f+" -> "+repr(sys.exc_info()[1])+"\n")
                
                # download objects from the bucket
                for obj in conn.get_container(bucket_name)[1]:
                    full_path = downloads_path+obj['name']
                    if not os.path.exists("/".join(full_path.split("/")[:-1])): # mkdir if it doesn't exist yet.
                        os.makedirs("/".join(full_path.split("/")[:-1]))
                    if not os.path.exists(full_path):
                        try:
                            start = time.time()
                            with open(full_path, 'w') as f:
                                f.write(conn.get_object(bucket_name, obj['name'])[1])
                            total = time.time()-start
                            time_array.append(total)
                            time_log.write("{0:.4f}".format(total).ljust(12)+str(obj['bytes']).ljust(12)+":downloading object - "+obj['name']+"\n")
                            file_size = os.path.getsize(full_path)
                            if obj['bytes'] != file_size:
                                with open(directories['logs']+'/errors.log', 'a') as error_log:
                                    error_log.write(provider+" | swift error on run "+str(i+1)+", '"+full_path+"' has a size of "+file_size+", expected "+obj['bytes']+"\n")
                        except:
                            with open(directories['logs']+'/errors.log', 'a') as error_log:
                                error_log.write(provider+" | swift error on run "+str(i+1)+" while downloading object: "+full_path+" -> "+repr(sys.exc_info()[1])+"\n")
                
                # remove the objects from the bucket
                for obj in conn.get_container(bucket_name)[1]:
                    try:
                        start = time.time()
                        conn.delete_object(bucket_name, obj['name'])
                        total = time.time()-start
                        time_array.append(total)
                        time_log.write("{0:.4f}".format(total).ljust(12)+str(obj['bytes']).ljust(12)+":deleting object - "+obj['name']+"\n")
                    except:
                        with open(directories['logs']+'/errors.log', 'a') as error_log:
                            error_log.write(provider+" | swift error on run "+str(i+1)+" while deleting object: "+obj['name']+" -> "+repr(sys.exc_info()[1])+"\n")
    
                # remove the bucket we created at the beginning of the script
                start = time.time()
                conn.delete_container(bucket_name)
                total = (time.time()-start)
                time_log.write("{0:.4f}".format(total).ljust(12)+":delete bucket\n")
                    
                total_time = sum(time_array)
                time_log.write("----------\n")
                time_log.write("{0:.4f}".format(total_time).ljust(12)+":total time for operations\n")
        
                time_log.write("\n\n")
        
                print provider+" using the swift api on "+uploads_path[:-1]+", run "+str(i+1)+" has finished..."
            # clean up the downloads directory if 'clean_downloads'
            if (clean_downloads):
                # remove the downloads directory and recreate it to make sure we start from scratch
                if os.path.exists(directories['downloads']):
                    shutil.rmtree(directories['downloads'])
                os.makedirs(directories['downloads'])
    

if __name__ == "__main__":
    # directories the program expects to be in place.  do not change unless you know what you are doing...
    directories = dict({'uploads':'uploads', 'downloads':'downloads', 'logs':'logs'})

    for d in directories.itervalues():
        if not os.path.exists(d):
            os.makedirs(d)
    
    # run the test cases
    for test_case in test_cases:
        for api in test_case['apis']:
            if test_case['provider'] in connections and api in connections[test_case['provider']]:
                connection = connections[test_case['provider']][api]
                if api == 's3':
                    s3_api(re.sub(r'\W+', '_', test_case['provider'].lower()), connection, directories, test_case['runs'], unique_container_name)
                if api == 'swift':
                    swift_api(re.sub(r'\W+', '_', test_case['provider'].lower()), connection, directories, test_case['runs'], unique_container_name)
            