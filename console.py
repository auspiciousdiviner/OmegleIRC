"""
This file is for manual omegling from the terminal emulator, implements simple threading with race conditions (printing, obviously)
"""
import time

from threading import Thread

import Omegle

def pollEvents(StrangerID):
    while True:
        Events = Omegle.getEvent(StrangerID)
        
        for Event in Events:
            
            if Event[0] == "waiting":
                print("Waiting...")
            
            elif Event[0] == "connected":
                print("Connected to stranger!")
                
            elif Event[0] == "typing":
                print("Stranger is typing...")
                
            elif Event[0] == "gotMessage":
                print("Stranger: {0}".format(Event[1]))
            
            elif Event[0] == "strangerDisconnected":
                print("Stranger disconnected!")
                break
                
            # Dunno what to do with the status info and ident digests just yet but someone could find a use out of them    
            elif Event[0] == "statusInfo":
                print("Received status info.")
                
            elif Event[0] == "identDigests":
                print("Received ident digests.")
            
            # Like recaptcha for instance
            else:
                print("Extraneous event: {0}\n".format(Event))       
            
            
def chat():
    StrangerID = Omegle.startSession()

    if StrangerID == "":
        print("Error, network is down or nobody wanted to chat.\n")
    
    else:
        print("Started session with the ID: {0}\n".format(StrangerID) )
        EventsThread = Thread(target=pollEvents, args=[StrangerID])
        EventsThread.start()

        while EventsThread.isAlive():
                
            Message = input("> ")
            
            # We "start typing" after we get our message because omeglers will think we've been typing for a long time
            # when infact we've been waiting for their message (learned this the hard way, lost lots of potential friends ;_;)
            Omegle.startTyping(StrangerID)
            
            time.sleep(len(Message) / 8) # Typing at eight characters a second
            
            Omegle.say(Message, StrangerID)
            
            Omegle.stopTyping(StrangerID)

    Omegle.endSession(StrangerID)
    
while True:
    print("1. Chat to a omegler\n2. Quit\n")
    
    Choice = input("What do you want to do? ")
    print("\n")
    
    if Choice == "1":
        chat()
    
    elif Choice == "2":
        break
        
    else:
        print("Invalid decision!")
    
    
