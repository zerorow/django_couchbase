
from django.core.cache import cache
from django.http import HttpResponse
import json
import couchbase
import time

class ClassA:
    def __init__(self):
        self._isa = True

class HelloWorld:
    def __init__(self):
        self._a = 'a'
        self._b = 'b'
        self._ClassA = ClassA()


def testcache( request ):
    key1 = "key1"
    #cache._cache.default_format = couchbase.FMT_PICKLE
    cache.delete( key1 ) # cleanup
    rslt = {}
    content1 = cache.get( key1 )
    assert( content1 == None )

    cache.set( key1, "Hello" )
    content1 = cache.get( key1 )
    assert( content1 != None )

    cache.set( key1, "Hello", timeout= -3 )
    content1 = cache.get( key1 )
    assert( content1 == None )

    cache.set( key1, "Hello" )
    cache.set_many( dict( key1= "Hello"), timeout= -3 )
    content1 = cache.get( key1 )
    assert( content1 == None )
    
    cache.set( key1, "Hello" )
    cache.delete_many( [key1] )
    content1 = cache.get( key1 )
    assert( content1 == None )

    cache.add( key1, "new value", timeout = -1)
    content1 = cache.get( key1 )
    content1 = cache.get( key1 )
    assert( content1 == None )

    cache.add( key1, 'value' ) 
    cache.add( key1, "new value" )
    content1 = cache.get( key1 )
    assert( content1 == 'value' )

    content1 = cache.get( key1 )
    cache.add( key1, "new value", timeout = -1)
    content1 = cache.get( key1 )
    assert( content1 == 'value' )

    key2 = 'key2'
    cache.set( key2, 'value2' )
    content2 = cache.get_many( [key1, key2] )


    if cache._cache.default_format == couchbase.FMT_PICKLE:
        myVar = HelloWorld()
        cache.set( 'obj', myVar )
        getVar = cache.get( 'obj' )
        assert( getVar != None )

    cache._cache.default_format == couchbase.FMT_JSON
    t1 = time.time()
    for i in xrange ( 0, 1000):
        ct = cache.get( key1 )
    t2 = time.time() 
    cache._cache.default_format == couchbase.FMT_PICKLE
    for i in xrange ( 0, 1000):
        ct = cache.get( key1 )
    t3 = time.time() 

    # Json format always fast than Pickle format, but not too much 
    #Json time: 1.8490   Pickle time: 2.0990
    #Json time: 1.7270   Pickle time: 1.7460
    #Json time: 1.6790   Pickle time: 1.7430
    print( "Json time: %.4f   Pickle time: %.4f"%( t2 - t1, t3 -t2 ) )

    # get in 2 times
    #Json time: 0.0030000   Pickle time: 0.0039999
    # get in 1 times
    #Json time: 0.0010002   Pickle time: 0.0019999
    # pickle as fast as json after first time startup

    return HttpResponse("OK")
