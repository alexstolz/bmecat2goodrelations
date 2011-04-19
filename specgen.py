#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""specgen.py

Generates HTML spec for proprietary classification in RDF/XML

Created by Alex Stolz on 2011-04-19
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
from rdflib import *
from jinja2 import *
import os

FOAF = Namespace("http://xmlns.com/foaf/0.1/")

def get_subElements(g, e, t):
    """Get a list of all subelements that belong to the given element"""
    subElements = []
    for se in g.subjects(t, e): # has subElements
        if type(se) is URIRef:
            se_uri = str(se)
            subElements.append(se_uri)
    subElements.sort(lambda a, b: cmp(a.lower(), b.lower()))
    return subElements

def pretty_list(l):
    """Bring the passed list to a suitable format and return the formatted string with anchor links"""
    pretty_format = ""
    if type(l) is list:
        l.sort() # sort the list alphabetically
        for item in l:
            # navigation in html document, if VOCAB ontology base uri is found
            item_idf = item[item.find("#"):]
            pretty_format += " <a href=\"%s\">%s</a>" % (item_idf, item_idf)
    return pretty_format

def create_html(output_dir):
    """Create HTML representation for product classification, if available"""
    
    if not os.path.exists("%s/rdf/catalog.rdf" % output_dir):
        return
    
    catalog_file = "%s/rdf/catalog.rdf" % output_dir
    
    html = open("%s/rdf/catalog.html" % output_dir, "w")
    
    loader = FileSystemLoader(".")
    env = Environment(loader=loader)
    template_classes = env.get_template("catalog.tmpl.html")
    
    g = ConjunctiveGraph()
    g.parse(catalog_file, format="xml")
    classes = []
    
    for c in g.subjects(RDF.type, OWL.Class):
        if type(c) is URIRef:
            uri = str(c)
            idf = uri[uri.find("#")+1:]
            label = g.value(c, RDFS.label)
            comment = g.value(c, RDFS.comment)
            subclassof = get_subElements(g, c, RDFS.subClassOf)
            depiction = g.value(c, FOAF.depiction)
            if depiction:
                depiction = """<img src="%(depiction)s" alt="" />""" % ({"depiction":depiction, "label":label})
            classes.append({"idf":idf, "label":label, "type_url":OWL.Class, "type":"owl:Class", "uri":uri, "depiction":depiction,
              "rdfs_subclassof":RDFS.subClassOf, "rdfs_comment":RDFS.comment, "comment":comment, "subclassof":pretty_list(subclassof)})
                
    html.write(template_classes.render({"classes":classes}).encode("utf-8"))
    

