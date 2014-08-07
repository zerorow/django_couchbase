"""
Memcached cache backend for Django using Coucbbase.

settings

    CACHES{
        'default'{ 'BACKEND': 'django_couchbase.memcached.CouchbaseCache',
                   'LOCATION': ['127.0.0.1:8091'],
                   'OPTIONS':{
                                'bucket': 'bk',
                                'password': 'password',
                                'operation_timeout': 20.5,
                                'gevent_support': False,
                                
                    # couchbase-cli need admin and password,
                    # but for security issue... be careful to use                    
                                'couchbase-cli': '/opt/couchbase/bin/python',
                                'admin': 'admin',
                                'admin-pwd': 'pwd'
                                }
                 }
          }


"""
import logging
import warnings
from threading import local

from django.conf import settings
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.cache.backends.memcached import BaseMemcachedCache

from couchbase import Couchbase,connection,exceptions

log = logging.getLogger('django.couchbase')

class CouchbaseCache(BaseMemcachedCache):
    def __init__(self, server, params, username=None, password=None):
        import os
        self._server = server
        self._client = None
        self._params = params
        self._couchbase_cli = ''
        self._bucket = ''
        super(CouchbaseCache, self).__init__(self._server, params, library=Couchbase,
                                           value_not_found_exception=ValueError)

    @property
    def _cache(self):
        # PylibMC uses cache options as the 'behaviors' attribute.
        # It also needs to use threadlocals, because some versions of
        # PylibMC don't play well with the GIL.
        client = self._client
        if client:
            return client
        host = None
        port = 8091
        if len(self._server) > 0:
            idx = self._server[0].find(':')
            host = self._server[0][:idx]
            port = self._server[0][idx+1:]

        if host == None:
            raise Exception('need host')

        self._couchbase_cli = self._options.get('couchbase-cli', '')
        self._bucket = self._options.get('bucket', 'default')
        client = self._lib.connect(  bucket= self._bucket,
                                     host=host,
                                     password=self._options.get('password', ''),
                                     port=port,
                                     timeout=self._options.get('operation_timeout', 10 ),
                                     lockmode=connection.LOCKMODE_WAIT, 
                                     experimental_gevent_support=self._options.get('gevent_support', False ) )

        self._client = client

        return client


    def get(self, key, default=None, version=None):
        try:
            rs = super(CouchbaseCache, self).get(key, default, version)
            return rs.value
        except Exception, e:
            #log.error('CouchbaseError: %s' % e, exc_info=True)
            return default



    def set(self, key, value, timeout=None, version=None):
        key = self.make_key(key, version=version)
        cn = self._cache
        rs = None
        
        try:
            #cn.lock( key,  ttl=self._get_memcache_timeout(timeout) )
            
            rs = cn.set(key, value,
                         ttl=self._get_memcache_timeout(timeout)
                        )
        except exceptions.KeyExistsError,e:
            #pass
            #cn.replace( key, value, ttl=self._get_memcache_timeout(timeout) ) 
            log.error( str(e) )
        except exceptions.NotFoundError:
            #pass
            #log.error('ServerError saving %s (%d bytes)' % (key, len(value)),
            #          exc_info=True)
            
            rs = self._cache.add(key, value, ttl=self._get_memcache_timeout(timeout) )
        except Exception, e:
            log.error('CouchbaseError: %s' % e, exc_info=True)
            rs = False

        return rs

    def add(self, key, value, timeout=0, version=None):
        key = self.make_key(key, version=version) 
        rs = False
        try:
            rs = self._cache.add(key, value, ttl=self._get_memcache_timeout(timeout) )
        except Exception, e:
            log.error( 'CouchbaseError: %s' % e, exc_info=True )
        return rs

    def close(self, **kwargs):
        pass        

    def delete(self, key, version=None):
        key = self.make_key(key, version=version) 
        rs = False
        try:
            rs = self._cache.delete(key)
        except Exception, e:
            pass
            #log.error( 'CouchbaseError: %s' % e, exc_info=True )
        return rs

    def incr(self, key, delta=1, version=None):
        key = self.make_key(key, version=version) 
        rs = False
        try:
            rs = self._cache.incr( key, delta )
        except exceptions.NotFoundError:
            rs = self._cache.add( key, delta, ttl=self._get_memcache_timeout(0) )
        except Exception, e:
            log.error( 'CouchbaseError: %s' % e, exc_info=True )
        return rs        

    def decr(self, key, delta=1, version=None):
        key = self.make_key(key, version=version) 
        rs = False
        try:
            rs = self._cache.decr( key, delta )
        except exceptions.NotFoundError:
            rs = self._cache.add( key, delta, ttl=self._get_memcache_timeout(0) )
        except Exception, e:
            log.error( 'CouchbaseError: %s' % e, exc_info=True )
        return rs

    def set_many(self, data, timeout=0, version=None):
        safe_data = {}
        for key, value in data.items():
            key = self.make_key(key, version=version)
            safe_data[key] = value
        rs = False    
        try:
            rs = self._cache.set_multi(safe_data, ttl=self._get_memcache_timeout(timeout))
        except Exception, e:
            log.error( 'CouchbaseError: %s' % e, exc_info=True )
        return rs

    def delete_many(self, keys, version=None):
        l = lambda x: self.make_key(x, version=version)
        rs = False
        try:
            rs = self._cache.delete_multi( map(l, keys) )
        except Exception, e:
            log.error( 'CouchbaseError: %s' % e, exc_info=True )
        return rs
            

    def clear(self):
        '''
         couchbase-cli
           To clear all data in bucket. use command couchbase-cli on Couchbase Server, 
           /opt/couchbase/bin/couchbase-cli bucket-flush -u admin -p password -c 127.0.0.1:8091 -b bucket --force
          
         Couchbase Command Line tools 
           folder  /opt/couchbase/lib/python could be copied to other host
           or get from GitHub
             > git clone https://github.com/couchbase/couchbase-cli.git 
           execute:
             > python couchbase-cli bucket-flush -u admin -p password -c 192.168.12.13:8091 -b bucket --force

        '''
        import os,os.path
        #if self._couchbase_cli == '':
        if True:
            log.error( 'CouchbaseError: please using couchbase-cli instead\n'
                    'couchbase-cli on GitHub\n'
                    'https://github.com/couchbase/couchbase-cli.git' )
            return False
        else:
            # Always 'Permission denied' ?
            return os.system( 'python %s bucket-flush -u %s -p %s -c %s -b %s --force'%
                        ( path.normpath( self._couchbase_cli + '/couchbaase-cli' ),
                        self._options.get( 'admin','' ),
                        self._options.get( 'admin-pwd', '' ),
                        self._server[0], self._bucket ) )== 0

        
