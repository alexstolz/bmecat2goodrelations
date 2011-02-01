#!/usr/bin/env python
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
    input_file = None
    base_uri = "http://www.example.com"
    output_folder = "output"
    catalog = classes.Catalog() # global settings are stored in catalog object
    
    # parse command line arguments
    previous = ""
    for arg in sys.argv[1:]:
        if previous == "-b":
            base_uri = arg
        elif previous == "-o":
            output_folder = arg
        elif previous == "" and arg[0] != '-':
            input_file = arg
        previous = ""
        if arg == "--help":
            print "Usage:"
            print "python main.py [-o <dir>] [-b <uri>] [--help]"
            print ""
            print "Option parameters:"
            print "-o <dir>\tcustomize location of output folder"
            print "\t\t(default = output)"
            print "-b <uri>\tdetermine base uri for deployment"
            print "\t\t(default = http://www.example.com)"
            print "--help\t\tprint usage summary"
            print ""
            print "..."
            print "LGPL licensed converter from BMECat XML to GoodRelations for Web publication"
            print "E-Business and Web Science Research Group, http://www.unibw.de/ebusiness/"
            print "..."
            return
        elif arg == "-b":
            previous = "-b"
        elif arg == "-o":
            previous = "-o"
            
    if not input_file:
        print "No XML input file was provided!"
        print "Usage summary: \"python main.py --help\""
        return
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer(output_folder, base_uri, catalog)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="offer")
    parserobject.parse(input_file, search="be")

    print "ready to serve"

if __name__ == "__main__":
    main()
