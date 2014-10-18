"""
Module for interfacing with Omegle
"""

import socket
from urllib.parse import urlencode

def send( Page, Message ):
    OmegleIP = socket.gethostbyname("omegle.com")
    
    Site = socket.socket()
    
    Site.connect((OmegleIP, 80)) # Omegle's IP address, plus port 80
    
    Site.send("POST /{0} HTTP/1.1\r\n".format(Page).encode('utf-8'))
    Site.send("Host: omegle.com\r\n".encode('utf-8'))
        
    # We need a message, if it's blank we will not get out stranger's ID
    if not Message:
        Message = "Hi"
    
    Site.send("Content-length: {0}\r\n".format(len(Message)).encode('utf-8'))
    Site.send("POSTDATA:{0}\r\n".format(Message).encode('utf-8'))
    Site.send("\r\n".encode('utf-8'))
    
    Recieved = Site.recv(8192)
    
    Site.close()
    
    return Recieved

def startSession():
    Recieved = send("start", "").split(b"\r\n")
    
    return Recieved[-2][8:-1].decode() # This returns the stranger ID

def say( Message, StrangerID ):
    send("send", "&msg={0}&id={1}".format(Message, StrangerID))

def getEvent( StrangerID ):
    Recieved = send("events", StrangerID).split(b"\r\n")
    
    return Recieved

def startTyping( StrangerID ):
    send("typing", "&id={0}".format(StrangerID))
    
def stopTyping( StrangerID ):
    send("typing", "&id={0}".format(StrangerID))
        
def endSession( StrangerID ):
    send("disconnect", "&id={0}".format(StrangerID))
    