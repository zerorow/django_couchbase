
from django.core.cache import cache
from django.http import HttpResponse
import json

def testcache( request ):
    key1 = "key1"
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

    return HttpResponse("OK")
    
    
    