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
# script with command line arguments: "python main.py file.xml -o output -b http://www.self-example.com/#" DONE
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
    image_uri = "ignore" # uri path to images as specified in bmecat catalog - ignore ignores any images
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
        elif previous == "-t":
            if arg == "actual":
                catalog.typeOfProducts = arg
        elif previous == "-i":
            image_uri = arg
        elif previous == "" and len(arg)>0 and arg[0] != '-':
            input_file = arg
        previous = ""
        if arg == "--help":
            print "USAGE"
            print "\tpython main.py [options] FILE"
            print
            print "OPTIONS"
            print "\t-o <dir>\t\tcustomize location of output folder"
            print "\t\t\t\t(default = output)"
            print "\t-b <uri>\t\tprovide base uri for deployment"
            print "\t\t\t\t(default = http://www.example.com)"
            print "\t-l <language>\t\t2-letter language code according to ISO 639-1"
            print "\t\t\t\t(default = try to determine from catalog)"
            print "\t-t <typeOfProduct>\tconfigure the type of product"
            print "\t\t\t\t(default = actual)"
            print "\t\t\t\tPossible values are [1]:"
            print "\t\t\t\t* actual: products are likely all gr:ActualProductOrServiceInstance, and"
            print "\t\t\t\t* placeholder: products are likely all gr:ProductOrServicesSomeInstancesPlaceholder"
            print "\t-i <uri>\t\tfull uri path to image folder that contains images as specified in bmecat file"
            print "\t\t\t\t(default = ignore)"
            print "\t--help\t\t\tprint usage summary"
            print
            print
            print "[1] http://www.heppnetz.de/ontologies/goodrelations/v1#ProductOrService"
            print
            print "..."
            print "LGPL licensed command-line script for the conversion of BMECat XML to GoodRelations for Web publishing"
            print "E-Business and Web Science Research Group, http://www.unibw.de/ebusiness/"
            print "Developer: Alex Stolz <alex.stolz@ebusiness-unibw.org>"
            print "..."
            return
        elif len(arg)>0 and arg[0] == "-":
            previous = arg
            
    if not input_file:
        print "No XML input file was provided!"
        print "Usage summary: \"python main.py --help\""
        return
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer(output_folder, base_uri, catalog, lang, image_uri)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="cataloggroup") # mappings between articles and catalog groups
    parserobject.parse(input_file, search="be")
    parserobject.parse(input_file, search="offer")

    print "ready to serve"

if __name__ == "__main__":
    main()
