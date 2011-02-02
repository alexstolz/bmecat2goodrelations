#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""main.py

Controlling module

Created by Alex Stolz on 2011-01-25
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""

# TODO:
# script with command line arguments: "python main.py file.xml -o output -b http://www.self-example.com/#"
# make py2exe, py2app
# let user choose between ProductOrServicesSomeInstancesPlaceholder and ActualProductOrServiceInstance
# eligibleCustomerTypes, Payment Methods, Warranty Promises?
import sys
import parser
import serializer
import classes

def main():
    """Main function"""
    # init
    lang = "" # else, use that from catalog!
    input_file = None # must be set by command line argument
    base_uri = "http://www.example.com" # may be overwritten by command line parameter
    output_folder = "output" # may be overwritten by command line parameter
    catalog = classes.Catalog() # global settings are stored in catalog object
    
    # parse command line arguments
    previous = ""
    for arg in sys.argv[1:]:
        if previous == "-b":
            base_uri = arg
        elif previous == "-o":
            output_folder = arg
        elif previous == "-l":
            lang = arg
        elif previous == "" and arg[0] != '-':
            input_file = arg
        previous = ""
        if arg == "--help":
            print "Usage:"
            print "python main.py [-o <dir>] [-b <uri>] [-l <language>] [--help]"
            print ""
            print "Option parameters:"
            print "-o <dir>\tcustomize location of output folder"
            print "\t\t(default = output)"
            print "-b <uri>\tdetermine base uri for deployment"
            print "\t\t(default = http://www.example.com)"
            print "-l <language>\t2-letter language code according to ISO 639-1"
            print "\t\t(default = try determine from catalog)"
            print "--help\t\tprint usage summary"
            print ""
            print "..."
            print "LGPL licensed converter from BMECat XML to GoodRelations for Web publication"
            print "E-Business and Web Science Research Group, http://www.unibw.de/ebusiness/"
            print "Developer: Alex Stolz <alex.stolz@ebusiness-unibw.org>"
            print "..."
            return
        elif arg == "-b":
            previous = "-b"
        elif arg == "-o":
            previous = "-o"
        elif arg == "-l":
            previous = "-l"
            
    if not input_file:
        print "No XML input file was provided!"
        print "Usage summary: \"python main.py --help\""
        return
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer(output_folder, base_uri, catalog, lang)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="cataloggroup") # mappings between articles and catalog groups
    parserobject.parse(input_file, search="offer")
    parserobject.parse(input_file, search="be")

    print "ready to serve"

if __name__ == "__main__":
    main()
