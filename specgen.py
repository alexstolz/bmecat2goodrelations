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
import codecs

FOAF = Namespace("http://xmlns.com/foaf/0.1/")

def get_isSubElementOf(g, e, t):
    """Get a list of all superelement URIs of a given element"""
    e = URIRef(e)
    se = g.value(e, t)
    se_list = []
    
    if type(se) is not URIRef: # subElementof is a collection
        for se_outer_element in g.objects(e, t): # get OWL:Class
            if type(se_outer_element) is BNode:
                for se_collection in g.objects(se_outer_element, OWL.unionOf):
                    superElements = list(g.items(se_collection))
                    for s in superElements:
                        s_uri = str(s)
                        se_list.append(s_uri)
        se = se_list
    else: # subelementof is no collection, but a sequence of "rdfs:subClassOf rdf:resource=..."
        for i in g.objects(e, t): # get all superElements of e
            if type(i) is URIRef:
                i_uri = str(i)
                se_list.append(i_uri)
        se = se_list
    
    return se

def pretty_list(l):
    """Bring the passed list to a suitable format and return the formatted string with anchor links"""
    pretty_format = ""
    if type(l) is list:
        l.sort() # sort the list alphabetically
        for item in l:
            # navigation in html document, if VOCAB ontology base uri is found
            item_idf = item
            if not "http://purl.org/goodrelations/v1#" in item:
                item_idf = item[item.find("#"):]
            pretty_format += " <a href=\"%s\">%s</a>" % (item_idf, item_idf)
    return pretty_format

def create_html(output_dir):
    """Create HTML representation for product classification, if available"""
    
    if not os.path.exists("%s/rdf/catalog.rdf" % output_dir):
        return
    
    print "found proprietary catalog structure - create html representation thereof"
    
    catalog_file = "%s/rdf/catalog.rdf" % output_dir
    
    html = codecs.open("%s/rdf/catalog.html" % output_dir, mode="w", encoding="utf-8")
    
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
            title = label[:label.find("(")].strip()
            comment = g.value(c, RDFS.comment)
            subclassof = get_isSubElementOf(g, c, RDFS.subClassOf)
            depiction = g.value(c, FOAF.depiction)

            if depiction:
                depiction = """<img src="%(depiction)s" alt="" />""" % ({"depiction":depiction, "label":label})
            else:
                depiction = ""
            classes.append({"idf":idf, "title":title, "label":label, "type_url":OWL.Class, "type":"owl:Class", "uri":uri, "depiction":depiction,
              "rdfs_subclassof":RDFS.subClassOf, "rdfs_comment":RDFS.comment, "rdfs_label":RDFS.label, "comment":comment, "subclassof":pretty_list(subclassof)})
                
    html.write(template_classes.render({"classes":classes}))
    

