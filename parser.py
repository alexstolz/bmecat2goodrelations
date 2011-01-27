#!/usr/bin/env python
"""parser.py

Parser module

Created by Alex Stolz on 2011-01-25
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
import xml.sax
import sys
from globvars import *

# global metadata: catalog language, kind (T_NEW_CATALOG, T_UPDATE_PRODUCTS, T_UPDATE_PRICES)

# businessentities: buyer, supplier, parties
# be metadata: duns, gln(=iln), address

# offers: article, product
# offers metadata: catalog language, currency, valid_start_date/end_date, territory

def processData(tag, product_open, company_open):
    """Catch information on-the-fly and store as objects"""
    global glob, be, bes, offer, offers
    #print tag.stack, tag.content
    top = tag.stack[-1]
    subtop = None
    if len(tag.stack) > 1:
        subtop = tag.stack[-2]
        
    # product tag has been opened immediately before
    if product_open:
        if offer != None:
            offers.append(offer)
        offer = Offer()
    # business entity tag has been opened immediately before
    if company_open:
        if be != None:
            bes.append(be)
        be = BusinessEntity()
    
    # check upper two items on stack -> should be enough
    if subtop == "CATALOG":
        if top == "LANGUAGE": glob.lang = tag.content
        elif top == "CURRENCY": glob.currency = tag.content
        elif top == "VALID_START_DATE": glob.validFrom = tag.content
        elif top == "VALID_END_DATE": glob.validThrough = tag.content
        elif top == "TERRITORY": glob.eligibleRegions = tag.content
    elif subtop == "PARTY" or subtop == "SUPPLIER" or subtop == "BUYER":
        if top == "PARTY_ID": be.id = tag.content
        elif top == "SUPPLIER_NAME" or top == "BUYER_NAME": be.legalName = tag.content
        elif top == "PARTY_ROLE": be.type = tag.content
    elif subtop == "ADDRESS":
        if top == "NAME": be.legalName = tag.content
        elif top == "STREET": be.street_address = tag.content
        elif top == "ZIP": be.postal_code = tag.content
        elif top == "BOXNO": be.postal_box = tag.content
        elif top == "CITY": be.location = tag.content
        elif top == "STATE": be.region = tag.content
        elif top == "COUNTRY": be.country_name = tag.content
        elif top == "PHONE": be.tel = tag.content
        elif top == "FAX": be.fax = tag.content
        elif top == "EMAIL": be.email = tag.content
        elif top == "URL": be.page = tag.content
    elif subtop == "PRODUCT" or subtop == "ARTICLE":
        if top == "SUPPLIER_PID" or top == "SUPPLIER_AID": offer.id = tag.content
    elif subtop == "PRODUCT_DETAILS" or subtop == "ARTICLE_DETAILS":
        if top == "DESCRIPTION_SHORT": offer.description = tag.content
        elif top == "DESCRIPTION_LONG": offer.comment = tag.content
        elif top == "EAN": offer.ean = tag.content
        elif top == "MANUFACTURER_PID": offer.manufacturer_id = tag.content
    elif subtop == "PRODUCT_ORDER_DETAILS":
        if top == "CONTENT_UNIT": offer.uom = tag.content
        if offer.uom == "" and top == "ORDER_UNIT": offer.uom = tag.content
    elif subtop == "PRODUCT_PRICE_DETAILS":
        if top == "VALID_START_DATE": offer.validFrom = tag.content
        elif top == "VALID_END_DATE": offer.validThrough = tag.content
    elif subtop == "PRODUCT_PRICE":
        if top == "PRICE_AMOUNT": offer.price = tag.content
        elif top == "PRICE_FACTOR": offer.price_factor = tag.content
        elif top == "PRICE_CURRENCY": offer.currency = tag.content
        elif top == "LOWER_BOUND": offer.product_quantity = tag.content
        elif top == "TERRITORY": offer.eligibleRegions = tag.content
    # elif subtop == "PRODUCT_FEATURE": # TODO

class EventHandler(xml.sax.ContentHandler):
    """Event handler of SAX Parser"""
    def __init__(self):
        self.attrs = None
        self.stack = []
        self.product_open = False
        self.company_open = False
    
    def startElement(self, name, attrs):
        """This function gets called on every tag opening event"""
        self.attrs = attrs
        self.stack.append(name)
        # check if offer or businessentity tag has been opened -> if opened, create new offer/business entity instance
        if name == "PRODUCT" or name == "ARTICLE":
            self.product_open = True
        elif name == "PARTY" or name == "SUPPLIER" or name == "BUYER":
            self.company_open = True
        
    def characters(self, ch):
        """This function gets called for each literal content within a tag"""
        ch = " ".join(ch.split())
        tag = Tag(self.stack, self.attrs, ch)
        processData(tag, self.product_open, self.company_open)
        # invalidate that tag has been opened
        self.product_open = False
        self.company_open = False

    def endElement(self, name):
        """This function gets called on every tag closing event"""
        self.stack.pop()
 
 
def parse(xml_file):
    """Parse given XML file"""
    # parse
    parser = xml.sax.make_parser()
    parser.setContentHandler(EventHandler())
    parser.parse(open(xml_file, "r"))
    #parser.parse(open("lieske_bmecat_unterhaltungselektronik.xml", "r"))

    # attach last found bes and offers
    if be != None:
        bes.append(be)
    if offer != None:
        offers.append(offer)
