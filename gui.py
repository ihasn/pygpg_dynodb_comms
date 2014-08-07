#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
#Import gnupg, getpass, urlib
import gnupg, getpass, urllib
#Import time stuff
from time import gmtime, strftime
import tkMessageBox

class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"User .gnupg directory")

        self.messageVariable = Tkinter.StringVar()
        self.message = Tkinter.Entry(self,textvariable=self.messageVariable)
        self.message.grid(column=0,row=1,sticky='EW')
        self.message.bind("<Return>", self.OnPressEnter)
        self.messageVariable.set(u"Message")


        button = Tkinter.Button(self,text=u"Open",
                                command=self.OnButtonClick)
        button.grid(column=1,row=0)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="white",bg="blue",wraplength=50)
        label.grid(column=0,row=4,columnspan=5,rowspan=4,sticky='EW')
        self.labelVariable.set(u"Output")

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry())       
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)


    def OnButtonClick(self):
        self.entry.focus_set()
        gpg = gnupg.GPG(binary='/usr/bin/gpg2', homedir=self.entryVariable.get())
        public_keys = gpg.list_keys()
        key_id = public_keys.fingerprints[0]
        encrypt_message = str(gpg.encrypt(self.messageVariable.get(), key_id))
        self.labelVariable.set(encrypt_message)
        tkMessageBox.showinfo('test', encrypt_message)
        self.entry.selection_range(0, Tkinter.END)

    def OnPressEnter(self,event):
        self.labelVariable.set( self.entryVariable.get()+" (You pressed ENTER)" )
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('GPG DynamoDB Comms')
    app.mainloop()
