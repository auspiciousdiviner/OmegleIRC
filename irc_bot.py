"""
This file is for omegling over irc with a bot! This too implements simple threading.
"""

import re
import socket
import time
from datetime import datetime

from threading import Thread

import Omegle

MessageQueue = [] # Messages you send to the stranger
ReplyQueue   = [] # Messages the stranger sends to you
InfoQueue    = [] # General messages the bot sends to you
LogQueue     = [] # Messages the bot saves to the Log

Chatting = False

Protocol = "tcp"
Address  = "irc.freenode.net"
Port     = 6667

Ident    = "Omegler"
Hostname = "Omegle"
Nick     = "SomeOmegler"
Realname = "Omegler"

Channel = "#amagital"

def pollReplyQueue(Socket):
    global ReplyQueue
    
    while Chatting and len(ReplyQueue) > 0:
        socketSend(Socket, "PRIVMSG {0} :{1}".format( Channel, ReplyQueue[0] + "\r\n"))
        ReplyQueue.pop(0)
    
def pollInfoQueue(Socket):
    global InfoQueue
    
    while Chatting and len(InfoQueue) > 0:
        socketSend(Socket, "PRIVMSG {0} :{1}".format( Channel, InfoQueue[0] + "\r\n"))
        InfoQueue.pop(0)
    
def pollLogQueue():
    global LogQueue
    
    while len(LogQueue) > 0:
        print(LogQueue[0].rstrip("\r"), end="")
        LogQueue.pop(0)

def pollEvents(StrangerID):
    global ReplyQueue, InfoQueue, LogQueue, Chatting
    
    while Chatting:
        Events = Omegle.getEvent(StrangerID)
        
        for Event in Events:
            
            if Event[0] == "waiting":
                InfoQueue.append("<Waiting...>")
            
            elif Event[0] == "connected":
                InfoQueue.append("<Connected to stranger!>")
                
            elif Event[0] == "typing":
                InfoQueue.append("<Stranger is typing...>")
                
            elif Event[0] == "gotMessage":
                ReplyQueue.append(Event[1])
            
            elif Event[0] == "strangerDisconnected":
                InfoQueue.append("<Stranger disconnected!>")
                Chatting = False
                break
                
            # Dunno what to do with the status info and ident digests just yet but someone could find a use out of them    
            elif Event[0] == "statusInfo":
                LogQueue.append("[{0}] Received status info.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
            elif Event[0] == "identDigests":
                LogQueue.append("[{0}] Received ident digests.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Like recaptcha for instance
            else:
                LogQueue.append("[{0}] Extraneous event: {1}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), Event))       
            
            
def chat():
    global MessageQueue, ReplyQueue, InfoQueue, Chatting
    
    StrangerID = Omegle.startSession()

    if StrangerID == "":
        InfoQueue.append("<Error, network is down or nobody wanted to chat.>")
    
    else:
        InfoQueue.append("<Started session!>")
        EventsThread = Thread(target=pollEvents, args=[StrangerID])
        EventsThread.start()

        while EventsThread.isAlive() and Chatting:
            while len(MessageQueue) > 0:
                Message = MessageQueue[0]
                
                # We "start typing" after we get our message because omeglers will think we've been typing for a long time
                # when infact we've been waiting for their message (learned this the hard way, lost lots of potential friends ;_;)
                Omegle.startTyping(StrangerID)
                
                time.sleep(len(Message) / 8) # Typing at eight characters a second
                
                print("Saying " + Message )
                Omegle.say(Message, StrangerID)
                
                Omegle.stopTyping(StrangerID)
                
                MessageQueue.pop(0) # Pop it when we're done with it!
            
    Omegle.endSession(StrangerID)

def socketSend( Socket, String ):
    "coverts a string to send to a socket"
    
    global LogQueue
    
    LogQueue.append("[{0}] {1}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), String))
    Socket.send( String.encode() )

IRC = socket.socket()
    
IRC.connect((Address, Port))
IRCFile = IRC.makefile()

ReplyQueueThread = Thread(target=pollReplyQueue, args=[IRC])
InfoQueueThread = Thread(target=pollInfoQueue, args=[IRC])
LogQueueThread = Thread(target=pollLogQueue)

while True:
    Line = IRCFile.readline()
    if Line.find("376"):
        break
    else:
        LogQueue.append("[Server] " + Line)
        
socketSend(IRC, "NICK {0}\r\n".format(Nick))
socketSend(IRC, "USER {0} {1} bla :{2}\r\n".format(Ident, Hostname, Realname))

socketSend(IRC, "JOIN {0}\r\n".format(Channel))

while True: #Max size of an IRC message (512) * the amount of bytes in a unicode string (4)

    Line = IRCFile.readline()
    
    if not Line:
        break
    
    MatchedObject = re.match(r'^PING (.*?)$', Line)
    if MatchedObject:
        socketSend(IRC, "PONG %s\r\n" % MatchedObject.group())
        LogQueue.append("[Server] " + Line)
    
    if re.search(r'!die', Line):
        socketSend(IRC, "QUIT :Dying...\r\n")
        LogQueue.append("[Server] " + Line)
        break
        
    elif re.search(r'!start', Line) and not Chatting:
        Chatting = True
        ChatThread = Thread(target=chat)
        ChatThread.start()
        if not ReplyQueueThread.isAlive():
            ReplyQueueThread = Thread(target=pollReplyQueue, args=[IRC])
            ReplyQueueThread.start()
            
        LogQueue.append("[Server] " + Line)
        
    elif re.search(r'!stop', Line) and Chatting:
        Chatting = False
        while ChatThread.isAlive():
            pass #no-op
        InfoQueue.append("<Stopped chatting>")
        
        LogQueue.append("[Server] " + Line)
        
    elif re.search(r'!say', Line) and Chatting:
        Message = Line[Line[1:].find(":") + 2:].rstrip('\n').rstrip('\r') # Gets the message, strips the newlines and carriage returns
        MessageQueue.append(Message)
        
        print("Adding " + Message + " to the message queue.")
        LogQueue.append("[Server] " + Line)
        
        
    else:
        LogQueue.append("[Server] " + Line)
        if not InfoQueueThread.isAlive():
            InfoQueueThread = Thread(target=pollInfoQueue, args=[IRC])
            InfoQueueThread.start()
        if not LogQueueThread.isAlive():
            LogQueueThread = Thread(target=pollLogQueue)
            LogQueueThread.start()
            
                