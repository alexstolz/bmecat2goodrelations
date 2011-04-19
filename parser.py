#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import time
import re

class Parser:
    """Parser class"""
    def __init__(self, serializer):
        """Initialization"""
        self.serializer = serializer
        self.catalog = serializer.catalog
        self.search = "be" # initialize to be, get modifications from parse function
        self.catalog_hierarchy = [] # will contain full catalog hierarchy
        self.article2categorygroup = Article2CatalogGroupMap()
        # initialize
        self.be = BusinessEntity()
        self.offer = Offer()
        self.catalog_group = CatalogGroup()
        self.product_feature = ProductFeature()
        self.feature = Feature()
        self.mime = Mime()
        
    def processCatalog(self, subtop, top, tag):
        if top == "CATALOG_STRUCTURE":
            if "type" in tag.attrs:
                if tag.attrs['type'] == "root": # root has no parents
                    self.catalog_group.parent_id = ""     
        if subtop == "CATALOG_STRUCTURE" and self.catalog_group != None:
            if top == "GROUP_ID":
                if tag.content != "":
                    self.catalog_group.id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)
            elif top == "GROUP_NAME":
                self.catalog_group.name = tag.content
            elif top == "GROUP_DESCRIPTION":
                self.catalog_group.description = tag.content
            elif top == "PARENT_ID":
                if tag.content != "":
                    self.catalog_group.parent_id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)          
        if subtop == "CATALOG_STRUCTURE" or ((len(tag.stack) > 2 and tag.stack[-3] == "CATALOG_STRUCTURE") or (len(tag.stack) > 3 and tag.stack[-4] == "CATALOG_STRUCTURE")) and self.catalog_group != None:
            if top == "MIME_PURPOSE":
                self.mime.name = tag.content
            if top == "MIME_DESCR":
                self.mime.desc = tag.content
            if top == "MIME_TYPE":
                self.mime.type = tag.content
            if top == "MIME_SOURCE":
                self.mime.source = tag.content

    def processArticle2CatalogGroupMap(self, subtop, top, tag):
        if subtop in ["PRODUCT_TO_CATALOGGROUP_MAP", "ARTICLE_TO_CATALOGGROUP_MAP"]:
            if top in ["PROD_ID", "ART_ID"]:
                self.article2categorygroup.article_id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)
            elif top == "CATALOG_GROUP_ID":
                if tag.content != "":
                    self.article2categorygroup.cataloggroup_id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)
        
    def processCompany(self, subtop, top, tag):
        if subtop in ["PARTY", "SUPPLIER", "BUYER"]:
            if top in ["PARTY_ID", "SUPPLIER_ID", "BUYER_ID"]:
                self.be.id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)
                if "type" in tag.attrs:
                    attr_type = tag.attrs['type']
                    if attr_type == "duns":
                        self.be.duns = tag.content
                    elif attr_type == "gln" or attr_type == "iln":
                        self.be.gln = tag.content
            elif top in ["SUPPLIER_NAME", "BUYER_NAME"]:
                self.be.legalName = tag.content
                if top == "SUPPLIER_NAME":
                    self.be.type = "supplier"
                else: self.be.type = "buyer"
            elif top == "PARTY_ROLE": self.be.type = tag.content
        if subtop == "ADDRESS":
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
        # supports two variants, where the second is definitely wrong, but in use anyway
        # SUPPLIER -> MIME_INFO -> MIME -> MIME_TYPE
        # SUPPLIER -> MIME -> MIME_TYPE (wrong usage)
        if subtop in ["PARTY", "SUPPLIER", "BUYER"] or ((len(tag.stack) > 2 and tag.stack[-3] in ["PARTY", "SUPPLIER", "BUYER"]) or (len(tag.stack) > 3 and tag.stack[-4] in ["PARTY", "SUPPLIER", "BUYER"])):
            if top == "MIME_PURPOSE":
                self.mime.name = tag.content
            if top == "MIME_DESCR":
                self.mime.desc = tag.content
            if top == "MIME_TYPE":
                self.mime.type = tag.content
            if top == "MIME_SOURCE":
                self.mime.source = tag.content
        
    def processOffer(self, subtop, top, tag):
        if subtop in ["PRODUCT", "ARTICLE"]:
            if top in ["SUPPLIER_PID", "SUPPLIER_AID"]:
                self.offer.id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)
                if "type" in tag.attrs:
                    attr_type = tag.attrs['type']
                    if attr_type == "ean":
                        self.offer.ean = tag.content
                    elif attr_type == "gtin":
                        self.offer.gtin = tag.content
                    elif attr_type == "upc":
                        self.offer.ean = "0" + tag.content # "0" + upc -> ean
        if subtop in ["PRODUCT_DETAILS", "ARTICLE_DETAILS"]:
            if top == "DESCRIPTION_SHORT": self.offer.description = tag.content
            elif top == "DESCRIPTION_LONG": self.offer.comment = tag.content
            elif top == "EAN": self.offer.ean = tag.content
            elif top == "INTERNATIONAL_PID": # replaces EAN and SUPPLIER_ALT_PID in BMECat 2005
                if "type" in tag.attrs:
                    attr_type = tag.attrs['type']
                    if attr_type == "ean":
                        self.offer.ean = tag.content
                    elif attr_type == "gtin":
                        self.offer.gtin = tag.content
                    elif attr_type == "upc":
                        self.offer.ean = "0" + tag.content # "0" + upc -> ean
            elif top in ["MANUFACTURER_PID", "MANUFACTURER_AID"]: self.offer.mpn = tag.content
            elif top == "MANUFACTURER_NAME":
                self.offer.manufacturer_id = re.sub(r"[^a-zA-Z0-9]", "", tag.content)
                self.offer.manufacturer_name = tag.content
            elif top in ["PRODUCT_STATUS", "ARTICLE_STATUS"]:
                if "type" in tag.attrs:
                    attr_type = tag.attrs['type']
                    if attr_type: # condition: used, new, ...
                        self.offer.condition = attr_type
        if subtop in ["PRODUCT_ORDER_DETAILS", "ARTICLE_ORDER_DETAILS"]:
            if top == "CONTENT_UNIT": self.offer.content_uom = tag.content
            if top == "ORDER_UNIT": self.offer.order_uom = tag.content
            if top == "NO_CU_PER_OU": self.offer.content_units = tag.content
            if top == "QUANTITY_MIN": self.offer.order_units = tag.content
        if subtop in ["PRODUCT_PRICE_DETAILS", "ARTICLE_PRICE_DETAILS"]:
            if top == "VALID_START_DATE": self.offer.validFrom = tag.content
            elif top == "VALID_END_DATE": self.offer.validThrough = tag.content
        if subtop in ["PRODUCT_PRICE", "ARTICLE_PRICE"]:
            if top == "PRICE_AMOUNT": self.offer.price = tag.content
            elif top == "PRICE_FACTOR": self.offer.price_factor = tag.content
            elif top == "PRICE_CURRENCY": self.offer.currency = tag.content
            elif top == "LOWER_BOUND": self.offer.price_lower = tag.content
            elif top == "TERRITORY": self.offer.eligibleRegions.append(tag.content)
        if subtop == "FEATURE":
            if top == "FNAME":
                self.feature.name = tag.content
            elif top == "FVALUE":
                self.feature.value = tag.content
            elif top == "FUNIT":
                self.feature.unit = tag.content
            elif top == "FREF":
                self.feature.fref = tag.content
        if subtop in ["PRODUCT", "ARTICLE"] or ((len(tag.stack) > 2 and tag.stack[-3] in ["PRODUCT", "ARTICLE"]) or (len(tag.stack) > 3 and tag.stack[-4] in ["PRODUCT", "ARTICLE"])):
            if top == "MIME_PURPOSE":
                self.mime.name = tag.content
            if top == "MIME_DESCR":
                self.mime.desc = tag.content
            if top == "MIME_TYPE":
                self.mime.type = tag.content
            if top == "MIME_SOURCE":
                self.mime.source = tag.content
        if subtop in ["PRODUCT_FEATURES", "ARTICLE_FEATURES"]:
            if top == "REFERENCE_FEATURE_SYSTEM_ID":
                self.product_feature.reference_feature_system_id = tag.content
            elif top == "REFERENCE_FEATURE_SYSTEM_NAME":
                self.product_feature.reference_feature_system_name = tag.content
            elif top == "REFERENCE_FEATURE_GROUP_NAME":
                self.product_feature.reference_feature_group_name = tag.content
            elif top == "REFERENCE_FEATURE_GROUP_ID":
                self.product_feature.reference_feature_group_id["value"] = tag.content
                if "type" in tag.attrs:
                    attr_type = tag.attrs['type']
                    if attr_type:
                        self.product_feature.reference_feature_group_id["type"] = attr_type
            elif top == "REFERENCE_FEATURE_GROUP_ID2":
                self.product_feature.reference_feature_group_id2["value"] = tag.content
                if "type" in tag.attrs:
                    attr_type = tag.attrs['type']
                    if attr_type:
                        self.product_feature.reference_feature_group_id2["type"] = attr_type
        
        if top in ["PRODUCT_PRICE", "ARTICLE_PRICE"]:
            if "price_type" in tag.attrs:
                attr_type = tag.attrs['price_type']
                if attr_type in ["net_list", "net_customer", "net_customer_exp", "net"]:
                    self.offer.taxes = "false"
                else:
                    self.offer.taxes = "true"
    
    def processData(self, tag, close):
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
            
        if self.search == "cataloggroup":
            if close["mime"]:
                if self.mime != None and self.mime.source != "" and self.catalog_group != None:
                    self.catalog_group.media.append(self.mime)
                self.mime = Mime() 
                
            # process catalog structure
            self.processCatalog(subtop, top, tag)
            # serialize catalog structure when be is processed, not with offers -> is supposed to be more performant
            if close["catalog"]:
                if self.catalog_group != None:
                    self.catalog_hierarchy.append(self.catalog_group)
                self.catalog_group = CatalogGroup()
            
            # mappings to catalog groups
            if close["mapping"]:
                if self.article2categorygroup.article_id != "" and self.article2categorygroup.cataloggroup_id != "":
                    self.article2categorygroup.save()
                self.article2categorygroup.article_id = ""
                self.article2categorygroup.cataloggroup_id = ""
            # process article to catalog group mapping
            self.processArticle2CatalogGroupMap(subtop, top, tag)
        
        elif self.search == "be":
            if close["mime"]:
                if self.mime != None and self.mime.source != "" and self.be != None:
                    self.be.media.append(self.mime)
                self.mime = Mime()
                #print "mime_close for supplier", top, subtop, tag.stack[-3], tag.content

            # business entity tag has been closed immediately before
            if close["company"]:
                if self.be != None and self.be.type == "supplier": # consider suppliers only
                    self.serializer.store(self.be, "be")
                self.be = BusinessEntity()
            # process company
            self.processCompany(subtop, top, tag)
            
        elif self.search == "offer":
            if close["mime"]:
                if self.mime != None and self.mime.source != "" and self.offer != None:
                    self.offer.media.append(self.mime)
                self.mime = Mime()
            # feature tag has been closed
            if close["feature"]:
                if self.feature != None and self.product_feature != None:
                    self.product_feature.features.append(self.feature)
                self.feature = Feature()
            # product feature tag has been closed
            if close["product_feature"]:
                if self.product_feature != None and self.offer != None:
                    self.offer.product_features.append(self.product_feature)
                self.product_feature = ProductFeature()
            # product tag has been closed immediately before
            if close["product"]: # and self.search == "offer":
                if self.offer != None:
                    self.offer.cataloggroup_ids = self.article2categorygroup.get(self.offer.id)
                    self.serializer.store(self.offer, "offer")
                self.offer = Offer()
            # process offering
            self.processOffer(subtop, top, tag)
        
    
    class EventHandler(xml.sax.ContentHandler):
        """Event handler of SAX Parser"""
        def __init__(self, outer):
            self.outer = outer
            self.attrs = {}
            self.stack = []
            self.close = {"product":False, "company":False, "feature":False, "catalog":False, "mapping":False, "mime":False, "product_feature":False}
            
        def falsify(self):
            """Helper function to set multiple vars to False"""
            for k in self.close:
                self.close[k] = False # when True, respective tag has been closed immediately
        
        def startElement(self, name, attrs):
            """This function gets called on every tag opening event"""
            self.attrs[name] = attrs
            self.stack.append(name)
            self.content = ""
            
        def characters(self, ch):
            """This function gets called for each literal content within a tag"""
            self.content = self.content + " ".join(ch.split())
    
        def endElement(self, name):
            """This function gets called on every tag closing event"""
            # check if offer or businessentity tag has been closed -> if closed, store offer/business entity instance
            if name in ["PRODUCT", "ARTICLE"]:
                self.close["product"] = True
            elif name in ["PARTY", "SUPPLIER", "BUYER"]:
                self.close["company"] = True
            elif name == "FEATURE":
                self.close["feature"] = True
            elif name == "CATALOG_STRUCTURE":
                self.close["catalog"] = True
            elif name in ["PRODUCT_TO_CATALOGGROUP_MAP", "ARTICLE_TO_CATALOGGROUP_MAP"]:
                self.close["mapping"] = True
            elif name == "MIME":
                self.close["mime"] = True
            elif name in ["PRODUCT_FEATURES", "ARTICLE_FEATURES"]:
                self.close["product_feature"] = True
                
            if type(self.content) == unicode:
                self.content = self.content.encode("utf-8")
            tag = Tag(self.stack, self.attrs[name], xml.sax.saxutils.unescape(self.content, {"&szlig;":"ß", "&auml;":"ä", "&ouml;":"ö", "&uuml;":"ü", "&Auml;":"Ä", "&Ouml;":"Ö", "&Uuml;":"Ü"}))
            self.outer.processData(tag, self.close)
            self.stack.pop()
            # set every close event to false
            self.falsify()
     
     
    def parse(self, xml_file, search="be"):
        """Parse given XML file"""
        self.search = search # search for be or for offer?
        
        # parse
        now = time.time()
        print "start parsing %s" % search
        parser = xml.sax.make_parser()
        parser.setFeature("http://xml.org/sax/features/external-general-entities", False)
        parser.setContentHandler(self.EventHandler(self))
        parser.parse(open(xml_file, "r"))
        print "finished with %s after %s seconds" %(search, str(time.time()-now))

        if len(self.catalog_hierarchy) > 0 and self.catalog_group != None:
            self.catalog_hierarchy.append(self.catalog_group)
            self.serializer.store(self.catalog_hierarchy, "catalog")
