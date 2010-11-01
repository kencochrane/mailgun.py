#coding: utf-8
"""
This module is an example of how to create and find/enum message routes 
using Mailgun API
"""
from mailgun import *
import urlparse

def main():
    Mailgun.init("key-afy6amxoo2fnj$u@mc")

    # lets make a catch-all route for all messages coming to @samples.mailgun.org
    # they will be HTTP POSTed to http://myhost/catch-all
    Route.make_new(pattern = "*@samples.mailgun.org", 
                   destination = "http://samples.mailgun.org/post").upsert()

    # but messages coming to press@myhost need to be redirected to my-mailbox@gmail.com
    route2 = Route()
    route2.pattern     = 'smtp@samples.mailgun.org'
    route2.destination = 'address@mailgun.info'
    route2.upsert()
   
    # and lets print out what we got:
    print "Routes:"
    for route in Route.find():
        print route.pattern, " ==> ", route.destination

if __name__ == "__main__":    
    main()
