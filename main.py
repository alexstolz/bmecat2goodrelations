#!/usr/bin/env python
"""main.py

Controlling module

Created by Alex Stolz on 2011-01-25
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""

# TODO:
# script with command line arguments: "python main.py file.xml"
# make py2exe, py2app
import parser
import serializer

def main():
    # parse
    parser.parse("2fclass_000076.xml")
    # serialize
    serializer.serialize()


if __name__ == "__main__":
    main()
    
