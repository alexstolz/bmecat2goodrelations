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
from classes import *

class Parser:
    """Parser class"""
    def __init__(self, serializer):
        """Initialization"""
        self.serializer = serializer
        self.catalog = serializer.catalog
        self.search = "be" # initialize to be, get modifications from parse function
        self.offers = [] # will contain offer ids for attachment to be
        
    def processCompany(self, subtop, top, tag):
        if subtop == "PARTY" or subtop == "SUPPLIER" or subtop == "BUYER":
            if top == "PARTY_ID" or top == "SUPPLIER_ID" or top == "BUYER_ID":
                self.be.id = tag.content
                if "type" in tag.attrs.keys():
                    attr_type = tag.attrs['type']
                    if attr_type == "duns":
                        self.be.duns = tag.content
                    elif attr_type == "gln" or attr_type == "iln":
                        self.be.gln = tag.content
            elif top == "SUPPLIER_NAME" or top == "BUYER_NAME":
                self.be.legalName = tag.content
                if top == "SUPPLIER_NAME":
                    self.be.type = "supplier"
                else: self.be.type = "buyer"
            elif top == "PARTY_ROLE": self.be.type = tag.content
        elif subtop == "ADDRESS":
            if top == "NAME": self.be.legalName = tag.content
            elif top == "STREET": self.be.street_address = tag.content
            elif top == "ZIP": self.be.postal_code = tag.content
            elif top == "BOXNO": self.be.postal_box = tag.content
            elif top == "CITY": self.be.location = tag.content
            elif top == "STATE": self.be.region = tag.content
            elif top == "COUNTRY": self.be.country_name = tag.content
            elif top == "PHONE": self.be.tel = tag.content
            elif top == "FAX": self.be.fax = tag.content
            elif top == "EMAIL": self.be.email = tag.content
            elif top == "URL": self.be.page = tag.content
        
    def processOffer(self, subtop, top, tag):
        if subtop == "PRODUCT" or subtop == "ARTICLE":
            if top == "SUPPLIER_PID" or top == "SUPPLIER_AID":
                self.offer.id = tag.content
                if "type" in tag.attrs.keys():
                    attr_type = tag.attrs['type']
                    if attr_type == "gtin":
                        self.offer.gtin = tag.content
        elif subtop == "PRODUCT_DETAILS" or subtop == "ARTICLE_DETAILS":
            if top == "DESCRIPTION_SHORT": self.offer.description = tag.content
            elif top == "DESCRIPTION_LONG": self.offer.comment = tag.content
            elif top == "EAN": self.offer.ean = tag.content
            elif top == "MANUFACTURER_PID" or top == "MANUFACTURER_AID": self.offer.mpn = tag.content
            elif top == "MANUFACTURER_NAME":
                self.offer.manufacturer_id = tag.content
                self.offer.manufacturer_name = tag.content
            elif top == "PRODUCT_STATUS" or top == "ARTICLE_STATUS":
                if "type" in tag.attrs.keys():
                    attr_type = tag.attrs['type']
                    if attr_type: # condition: used, new, ...
                        self.offer.condition = attr_type
        elif subtop == "PRODUCT_ORDER_DETAILS" or subtop == "ARTICLE_ORDER_DETAILS":
            if top == "CONTENT_UNIT": self.offer.content_uom = tag.content
            if top == "ORDER_UNIT": self.offer.order_uom = tag.content
            if top == "NO_CU_PER_OU": self.offer.content_units = tag.content
            if top == "QUANTITY_MIN": self.offer.order_units = tag.content
        elif subtop == "PRODUCT_PRICE_DETAILS" or subtop == "ARTICLE_PRICE_DETAILS":
            if top == "VALID_START_DATE": self.offer.validFrom = tag.content
            elif top == "VALID_END_DATE": self.offer.validThrough = tag.content
        elif subtop == "PRODUCT_PRICE" or subtop == "ARTICLE_PRICE":
            if top == "PRICE_AMOUNT": self.offer.price = tag.content
            elif top == "PRICE_FACTOR": self.offer.price_factor = tag.content
            elif top == "PRICE_CURRENCY": self.offer.currency = tag.content
            elif top == "LOWER_BOUND": self.offer.price_lower = tag.content
            elif top == "TERRITORY": self.offer.eligibleRegions.append(tag.content)
        elif subtop == "FEATURE":
            if top == "FNAME":
                self.feature.name = tag.content
            elif top == "FVALUE":
                self.feature.value = tag.content
            elif top == "FUNIT":
                self.feature.unit = tag.content
        elif top == "PRODUCT_PRICE" or top == "ARTICLE_PRICE":
            if "type" in tag.attrs.keys():
                attr_type = tag.attrs['type']
                if attr_type in ["net_list", "net_customer", "net_customer_exp", "net"]:
                    self.offer.taxes = "false"
                else:
                    self.offer.taxes = "true"
    
    def processData(self, tag, product_open, company_open, feature_open):
        """Catch information on-the-fly and store as objects"""
        top = tag.stack[-1]
        subtop = None
        if len(tag.stack) > 1:
            subtop = tag.stack[-2]
                    
        # check upper two items on stack -> should be enough
        if subtop == "CATALOG":
            if top == "LANGUAGE": self.catalog.lang = tag.content
            elif top == "CURRENCY": self.catalog.currency = tag.content
            elif top == "VALID_START_DATE": self.catalog.validFrom = tag.content
            elif top == "VALID_END_DATE": self.catalog.validThrough = tag.content
            elif top == "TERRITORY": self.catalog.eligibleRegions.append(tag.content)
            
        if self.search == "be":
            # business entity tag has been opened immediately before
            if company_open:
                if self.be != None:
                    self.be.offers = self.offers
                    self.serializer.store(self.be, "be")
                self.be = BusinessEntity()
            # process company
            self.processCompany(subtop, top, tag)
            
        elif self.search == "offer":
            # feature tag has been opened
            if feature_open:
                if self.feature != None and self.offer != None:
                    self.offer.features.append(self.feature)
                self.feature = Feature()
            # product tag has been opened immediately before
            if product_open and self.search == "offer":
                if self.offer != None:
                    self.serializer.store(self.offer, "offer")
                    self.offers.append(self.offer.id)
                self.offer = Offer()
            # process offering
            self.processOffer(subtop, top, tag)
        
    
    class EventHandler(xml.sax.ContentHandler):
        """Event handler of SAX Parser"""
        def __init__(self, outer):
            self.outer = outer
            self.attrs = None
            self.stack = []
            self.product_open = False # when True, product tag has been opened immediately
            self.company_open = False # when True, company tag has been opened immediately
            self.feature_open = False # when True, feature tag has been opened immediately
        
        def startElement(self, name, attrs):
            """This function gets called on every tag opening event"""
            self.attrs = attrs
            self.stack.append(name)
            # check if offer or businessentity tag has been opened -> if opened, create new offer/business entity instance
            if name == "PRODUCT" or name == "ARTICLE":
                self.product_open = True
            elif name == "PARTY" or name == "SUPPLIER" or name == "BUYER":
                self.company_open = True
            elif name == "FEATURE":
                self.feature_open = True
            
        def characters(self, ch):
            """This function gets called for each literal content within a tag"""
            ch = " ".join(ch.split())
            tag = Tag(self.stack, self.attrs, ch)
            self.outer.processData(tag, self.product_open, self.company_open, self.feature_open)
            # invalidate that tag has been opened
            self.product_open = False
            self.company_open = False
            self.feature_open = False
    
        def endElement(self, name):
            """This function gets called on every tag closing event"""
            self.stack.pop()
     
     
    def parse(self, xml_file, search="be"):
        """Parse given XML file"""
        self.search = search # search for be or for offer?
        self.be = None
        self.offer = None
        self.feature = None
        
        # parse
        parser = xml.sax.make_parser()
        parser.setContentHandler(self.EventHandler(self))
        parser.parse(open(xml_file, "r"))
        
        # write serialization for last found bes and offers
        if self.feature != None:
            self.offer.features.append(self.feature)
        if self.offer != None:
            self.serializer.store(self.offer, "offer")
            self.offers.append(self.offer.id)        
        if self.be != None:
            self.be.offers = self.offers
            self.serializer.store(self.be, "be")
