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
          
          self.InputKeysInitiateDBConnection()
      
        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=2-local_keys,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"User .gnupg directory")

        self.key_idLabelVariable = Tkinter.StringVar()
        key_id = Tkinter.Label(self,textvariable=self.key_idLabelVariable, anchor="w", fg="white", bg="blue",wraplength=50)
        key_id.grid(column=0,row=4-local_keys,sticky='EW')
        self.key_idLabelVariable.set(u"Key ID")

        self.messageVariable = Tkinter.StringVar()
        self.message = Tkinter.Entry(self,textvariable=self.messageVariable)
        self.message.grid(column=0,row=3-local_keys,sticky='EW')
        self.message.bind("<Return>", self.OnPressEnter)
        self.messageVariable.set(u"Message")

        button = Tkinter.Button(self,text=u"Encrypt", command=self.OnButtonClick)
        button.grid(column=1,row=0)

        send = Tkinter.Button(self, text=u"Send", command=self.SendMessage)
        send.grid(column=1,row=1)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable, anchor="w",fg="white",bg="blue",wraplength=50)
        label.grid(column=0,row=4-local_keys,columnspan=5,rowspan=4,sticky='EW')
        self.labelVariable.set(u"Output")

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
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

    def OnButtonClick(self):
        self.entry.focus_set()
        gpg = gnupg.GPG(binary='/usr/bin/gpg2', homedir=self.entryVariable.get())
        public_keys = gpg.list_keys()
        key_id = public_keys.fingerprints[0]
        self.key_idLabelVariable.set(key_id)
        encrypt_message = str(gpg.encrypt(self.messageVariable.get(), key_id))
        self.labelVariable.set(encrypt_message)
        self.entry.selection_range(0, Tkinter.END)

    def OnPressEnter(self,event):
        self.labelVariable.set( self.entryVariable.get()+" (You pressed ENTER)" )
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('GPG DynamoDB Comms')
    app.mainloop()

