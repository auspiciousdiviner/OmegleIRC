"""
Module for interfacing with Omegle
"""

import ast
import urllib.request
import urllib.parse

def send( Page, Message ):
    
    SiteRequest = urllib.request.Request( 'http://omegle.com/' + Page, urllib.parse.urlencode(Message).encode('utf-8') )
    SiteReponse = urllib.request.urlopen(SiteRequest)
    
    return SiteReponse.read()
    

def startSession():
    # not sure what the rcs means or why it works but it works! (I'm such a great programmer)
    Recieved = send("start", {"rcs" : 1})
    
    return Recieved[1:-1].decode() # This returns the stranger ID without having to parse the damned thing

def say( Message, StrangerID ):
    send("send", {'msg' : Message, 'id' : StrangerID})

def getEvent( StrangerID ):
    Received = send("events", {'id' : StrangerID}).decode()
    
    # We get null only if we're disconnected/invalid id
    if Received == 'null':
        return []
    
    else:
        return ast.literal_eval(Received) #decodes the string and parses it to a proper list

def startTyping( StrangerID ):
    send("typing", {'id' : StrangerID})
    
def stopTyping( StrangerID ):
    send("typing", {'id' : StrangerID})
        
def endSession( StrangerID ):
    send("disconnect", {'id' : StrangerID})
    