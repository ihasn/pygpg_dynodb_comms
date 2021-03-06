#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
#Import gnupg, getpass, urlib
import gnupg, getpass, urllib
#Import time stuff
from time import gmtime, strftime
import tkMessageBox
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
import ScrolledText

class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        tkMessageBox.askquestion("Use Local AWS Keys", "Use Local AWS Keys", icon='warning')

        if 'yes':
          self.LocalKeysInitiateDBConnection()
          local_keys = 2
        else:
          self.entryAWSKeyVariable = Tkinter.StringVar()
          self.entryAWSKey = Tkinter.Entry(self, textvariable=self.entryAWSKeyVariable)
          self.entryAWSKey.grid(column=0,row=0,sticky='EW')
          self.entryAWSKeyVariable.set(u"AWS Key")

          self.entryAWSSecretVariable = Tkinter.StringVar()
          self.entryAWSSecret = Tkinter.Entry(self, textvariable=self.entryAWSSecretVariable)
          self.entryAWSSecret.grid(column=0,row=1,sticky='EW')
          self.entryAWSSecretVariable.set(u"AWS Secret Key")
          local_keys = 0
          self.InputKeysInitiateDBConnection()
      
        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=2-local_keys,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"User .gnupg directory")

        self.key_idLabelVariable = Tkinter.StringVar()
        self.key_id = Tkinter.Label(self,textvariable=self.key_idLabelVariable, anchor="w",wraplength=500)
        self.key_id.grid(column=0,row=3-local_keys,sticky='EW')
        self.key_idLabelVariable.set(u"Key ID")

        self.messageVariable = Tkinter.StringVar()
        self.message = Tkinter.Entry(self,textvariable=self.messageVariable)
        self.message.grid(column=0,row=4-local_keys,sticky='EW')
        self.message.bind("<Return>", self.OnPressEnter)
        self.messageVariable.set(u"Message")

        button = Tkinter.Button(self,text=u"Activate", command=self.OnButtonClick)
        button.grid(column=1,row=0)

        send = Tkinter.Button(self, text=u"Send", command=self.SendMessage)
        send.grid(column=1,row=1)

        recieve = Tkinter.Button(self, text=u"Recieve", command=self.OnRecieveClick)
        recieve.grid(column=1,row=2)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Message(self,textvariable=self.labelVariable, anchor="w")
        label.grid(column=0,row=10-local_keys,rowspan=10,sticky='EW')
        self.labelVariable.set(u"Output")

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,True)
        self.update()
        self.geometry(self.geometry())       
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def InputKeysInitiateDBConnection(self):
        self.gpgcomms = Table('comms',connection= boto.dynamodb2.connect_to_region("us-east-1", aws_access_key_id=self.entryAWSKeyVariable.get(), aws_secret_access_key=self.entryAWSSecretVariable.get()))

    def LocalKeysInitiateDBConnection(self):
        self.gpgcomms = Table('comms')

    def SendMessage(self):
        self.gpgcomms.put_item(data={'key_id': self.key_idLabelVariable.get(), 'time': strftime("%Y%m%d%H%M%S", gmtime()), 'message': self.labelVariable.get(), 'read': '0'})
        tkMessageBox.showinfo("Sent", "Message sent to DB")

    def RecieveMessage(self):
        results = self.gpgcomms.query_2(self.key_idLabelVariable.get())
        tkMessageBox.message("Password is", passowrd, icon='warning')
        #for messages in results:
          #pulled_encrypt_message = message['message']


    def InitGPG(self):
        self.gpg = gnupg.GPG(binary='/usr/bin/gpg2', homedir=self.entryVariable.get())
        public_keys = self.gpg.list_keys()
        key_id = public_keys.fingerprints[0]
        self.key_idLabelVariable.set(key_id)

    def OnButtonClick(self):
        self.entry.focus_set()
        self.InitGPG()
        encrypt_message = str(self.gpg.encrypt(self.messageVariable.get(), self.key_idLabelVariable.get()))
        self.labelVariable.set(encrypt_message)
        self.entry.selection_range(0, Tkinter.END)

    def OnPressEnter(self,event):
        self.labelVariable.set( self.entryVariable.get()+" (You pressed ENTER)" )
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def OnRecieveClick(self):
        self.entry.focus_set()
        password = Password(self)
        self.wait_window(password.top)
        self.RecieveMessage()

class Password:
    def __init__(self, parent):
        Tkinter.Tk(None)
        self.parent = parent

        self.messageVariable = Tkinter.StringVar()
        self.message = Tkinter.Entry(self,textvariable=self.messageVariable)
        self.message.grid(column=0,row=4-local_keys,sticky='EW')
        self.messageVariable.set(u"Password")

        b = Button(password, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):

        print "value is", self.e.get()
        self.ok.destroy()

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('GPG DynamoDB Comms')
    app.mainloop()

