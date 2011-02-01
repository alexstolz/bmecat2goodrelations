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
import parser
import serializer
import classes

def main():
    """Main function"""
    # init
    input_file = "fclass_000076.xml"#"bmecat_ikea_input.xml" #
    output_folder = "output"
    catalog = classes.Catalog() # global settings are stored in catalog object
    
    # parse and serialize on-the-fly
    serializerobject = serializer.Serializer("output", "http://www.example.de", catalog)
    parserobject = parser.Parser(serializerobject)
    parserobject.parse(input_file, search="offer")
    parserobject.parse(input_file, search="be")


if __name__ == "__main__":
    main()
