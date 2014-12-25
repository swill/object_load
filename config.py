# setup the different connections you want to test.  
# if you change the name of the connections, change the provider name in the test cases...
connections = {
    #'DreamHost': {
    #    's3': {
    #        'host':'objects.dreamhost.com',
    #        'port':8080,
    #        'access_key':'xxxxxxxxxxxxxxxxxxxx', 
    #        'secret_key':'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    #    },
    #    'swift': {
    #        'auth_url':'https://objects.dreamhost.com:8080/auth',
    #        'username':'user:user',
    #        'api_key':'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    #    }
    #},
    #'AWS': {
    #    's3': {
    #        'host':'s3.amazonaws.com',
    #        'access_key':'xxxxxxxxxxxxxxxxxxxx', 
    #        'secret_key':'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    #    }
    #}
}

# setup the test cases you want to run.
# if you changed the names of the connections, change the provider name here...
test_cases = [
    #{
    #    'provider':'DreamHost',
    #    'apis': ['s3', 'swift'],
    #    'runs': [
    #        {'directory':'small', 'batch_size':0, 'max_graph_time':1},
    #        {'directory':'medium', 'batch_size':5, 'max_graph_time':100}
    #    ]
    #},
    #{
    #    'provider':'AWS',
    #    'apis': ['s3'],
    #    'runs': [
    #        {'directory':'small', 'batch_size':0, 'max_graph_time':1},
    #        {'directory':'medium', 'batch_size':5, 'max_graph_time':100}
    #    ]
    #}
]

column_width = 550 # the column width in pixels in the `html/index.html` file.
unique_container_name = 'global_unique_bucket_name' # this is the default.  this container will be removed after execution.

# appending a hash to the end of the bucket name to make it harder for it to collide with any container in your environment...
unique_container_name = '%s_%s' % (unique_container_name, '5fc6a13455bdba81f5f36cff6450d71305f8d24d')

