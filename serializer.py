#!/usr/bin/env python
"""serializer.py

Serializes arrays of classes as RDF/XML

Created by Alex Stolz on 2011-01-26
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
from globvars import *

def serialize():
    """Serialize array of objects"""
    global glob, bes, offers
    
    # debug output
    for be in bes:
        print "B: ", be.id, " -> ", be.legalName
    for offer in offers:
        print "O: ", offer.id, " -> ",  offer.description