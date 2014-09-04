Use couchbase as Django cache engine
====
    install
        pip install django_couchbase
    
    settings
        
        USE_COUCHBASE = True
        if USE_COUCHBASE:
            CACHES['default']['BACKEND']= 'django_couchbase.memcached.CouchbaseCache'
            CACHES['default']['LOCATION'] = ['127.0.0.1:8091']
            CACHES['default']['OPTIONS'] = {
                                            'bucket': 'bk',
                                            'password': 'password',
                                            'operation_timeout': 20.5,
                                            'gevent_support': False,
                                            'format': 'PICKLE'
                                            }
