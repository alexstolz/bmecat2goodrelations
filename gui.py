#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""gui.py

Graphical User Interface

Created by Alex Stolz on 2011-03-14
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
import parser
import serializer
import classes
from Tkinter import *
from tkFileDialog import askdirectory, askopenfilename
import sys

class TextStdout:
    '''A class for redirecting stdout to Text widget.'''
    def write(self,str):
        textarea.insert(0.0, str)
        textarea.update_idletasks()

class TextStderr:
    '''A class for redirecting stderr to Text widget.'''
    def write(self,str):
        textarea.insert(0.0, "\nERROR: %s" % str)
        textarea.update_idletasks()
        
sys.stdout = TextStdout()
sys.stderr = TextStderr()

def chooseInputFile():
    entries[0].delete(0, END)
    entries[0].insert(0, askopenfilename(filetypes=[("xmlfiles","*.xml")]))

def chooseOutputFolder():
    entries[3].delete(0, END)
    entries[3].insert(0, askdirectory())
    
def convert():
    """Main function"""    
    input_file = None # must be set by command line argument
    lang = "" # else, use that from catalog!
    base_uri = "http://www.example.com" # may be overwritten by command line parameter
    output_folder = "output" # may be overwritten by command line parameter
    image_uri = "ignore" # uri path to images as specified in bmecat catalog - ignore ignores any images
    model_only = False # print model data only, i.e. hide/skip offering details
    pattern = "" # product uri pattern, any string containing %s is allowed, e.g. http://www.example.com/products/id_%s/
    catalog = classes.Catalog() # global settings are stored in catalog object

    if entries[0].get():
        input_file = entries[0].get()  
    if entries[1].get():
        base_uri = entries[1].get()
    if entries[2].get():
        image_uri = entries[2].get()
    if entries[3].get():
        output_folder = entries[3].get()
    if entries[4].get():
        lang = entries[4].get()
    if entries[5].get() == "actual":
        catalog.typeOfProducts = entries[5].get()
    elif entries[5].get() == "placeholder":
        catalog.typeOfProducts = entries[5].get()
    elif entries[5].get() == "model":
        model_only = True
    elif entries[5].get():
        print "WARNING: Could not interpret supplied product type -> %s" % entries[5].get()
    if entries[6].get() != None:
        pattern = entries[6].get()
       
    if not input_file:
        sys.stderr.write("No XML input file was provided")
        return -1
    
    print "Conversion started... please wait"
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer(output_folder, base_uri, catalog, lang, image_uri, model_only, pattern)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="cataloggroup") # mappings between articles and catalog groups
    parserobject.parse(input_file, search="be")
    parserobject.parse(input_file, search="offer")

    print "Conversion successfully finished"

# graphical ui with tkinter
root = Tk()
root.title("BMECat2GoodRelations Converter")
entries = []

label_texts = ["Input File", "Base URI", "URI path for images", "Output folder location", "Catalog language", "Product type", "Product URL pattern"]

i = 0
for text in label_texts:
    l = Label(root, text=text)
    l.grid(row=i, sticky=W)
    
    e = Entry(root, width=60)
    e.grid(row=i, column=1)
    entries.append(e)
    
    if text == "Input File":
        b = Button(root)
        b.grid(row=i, column=2, sticky=S)
        b["text"] = "choose .."
        b["command"] = chooseInputFile
    elif text == "Output folder location":
        b = Button(root)
        b.grid(row=i, column=2, sticky=S)
        b["text"] = "choose .."
        b["command"] = chooseOutputFolder
    
    i = i+1

b = Button(root)
b.grid(row=(i+1), columnspan=3, sticky=S)
b["text"] = "Start conversion"
b["command"] = convert # call on event
#status = Label(root, text="", bd=1, relief=SUNKEN, anchor=W)
#status.grid(row=(i+2), columnspan=3, sticky=E+W)
scrollbar = Scrollbar(root, orient=VERTICAL)
textarea = Text(root, height=20, borderwidth=6, foreground='white', background='black',
                yscrollcommand=scrollbar.set)
textarea.grid(row=(i+2), columnspan=3, sticky=N+S+E+W)
scrollbar.config(command=textarea.yview)
root.mainloop()

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__