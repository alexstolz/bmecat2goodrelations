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
from StringIO import StringIO

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
    else:
        print "WARNING: could not interpret product type ->", entries[5].get()
        
    if not input_file:
        status.config(text="No XML input file was provided!")
        status.update_idletasks()
        return
    
    status.config(text="conversion started... please wait")
    status.update_idletasks()
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer(output_folder, base_uri, catalog, lang, image_uri, model_only)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="cataloggroup") # mappings between articles and catalog groups
    parserobject.parse(input_file, search="offer")
    parserobject.parse(input_file, search="be")

    status.config(text="conversion finished")
    status.update_idletasks()

# graphical ui with tkinter
root = Tk()
root.title("BMECat2GoodRelations converter")

label_texts = ["Input File", "Base URI", "URI path for images", "Output folder location", "Catalog language", "Product type"]
entries = []


i = 0
for text in label_texts:
    l = Label(root, text=text)
    l.grid(row=i, sticky=W)
    
    e = Entry(root)
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
status = Label(root, text="", bd=1, relief=SUNKEN, anchor=W)
status.grid(row=(i+2), columnspan=3, sticky=E+W)
root.mainloop()
