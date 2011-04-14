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
# configurable foaf:page element -> pattern: http://www.weidmueller.de/?Page=Product&Product_id=[<ID>] DONE
# think about UOM!! -> mm should be MMT! -> maybe provide a python dict with mappings
# support hash and slash uris!
# script with command line arguments: "python main.py file.xml -o output -b http://www.self-example.com/#" DONE
# make py2exe, py2app
# let user choose between ProductOrServicesSomeInstancesPlaceholder and ActualProductOrServiceInstance DONE
# eligibleCustomerTypes, Payment Methods, Warranty Promises? - maybe best trade-off not to use them for sake of complexity avoidance
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
    model_only = False # print model data only, i.e. hide/skip offering details
    pattern = "" # product uri pattern, any string containing %s is allowed, e.g. http://www.example.com/products/id_%s/
    catalog = classes.Catalog() # global settings are stored in catalog object
    
    # parse command line arguments
    previous = ""
    for arg in sys.argv[1:]:
        warn = False
        if previous == "-b":
            base_uri = arg
        elif previous == "-o":
            output_folder = arg
        elif previous == "-l":
            lang = arg
        elif previous == "-t":
            if arg == "actual":
                catalog.typeOfProducts = arg
            elif arg == "placeholder":
                catalog.typeOfProducts = arg
            elif arg == "model":
                model_only = True
            else:
                warn = True
        elif previous == "-i":
            image_uri = arg
        elif previous == "-p":
            pattern = arg
        elif previous == "" and len(arg)>0 and arg[0] != '-':
            input_file = arg
        elif previous:
            warn = True
            
        if warn:
            print "WARNING: Could not interpret command series -> %s %s" % (previous, arg)
            
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
            print "\t-t <typeOfProduct>\tconfigure the type of product (if \"model\", then will print product model catalog only)"
            print "\t\t\t\t(default = actual)"
            print "\t\t\t\tPossible values are [1]:"
            print "\t\t\t\t* actual: products are likely all gr:ActualProductOrServiceInstance, and"
            print "\t\t\t\t* placeholder: products are likely all gr:ProductOrServicesSomeInstancesPlaceholder"
            print "\t\t\t\t* model: only product model data (gr:ProductOrServiceModel) gets printed out, i.e. offer data is skipped"
            print "\t-i <uri>\t\tfull uri path to image folder that contains images as specified in bmecat file"
            print "\t\t\t\t(default = ignore)"
            print "\t-p <uri_pattern>\turi pattern for product page urls"
            print "\t\t\t\t(default = \"\")"
            print "\t\t\t\tproduct uri pattern, any string containing %s is allowed, e.g. http://www.example.com/products/id_%s/"
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
        sys.stderr.write("No XML input file was provided")
        print "Usage summary: \"python main.py --help\""
        return
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer(output_folder, base_uri, catalog, lang, image_uri, model_only, pattern)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="cataloggroup") # mappings between articles and catalog groups
    parserobject.parse(input_file, search="be")
    parserobject.parse(input_file, search="offer")

    print "Conversion successfully finished"

if __name__ == "__main__":
    main()
