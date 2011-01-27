#!/usr/bin/env python
"""classes.py

Defines classes

Created by Alex Stolz on 2011-01-26
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""

class Global():
    """Global settings"""
    def __init__(self):
        self.lang = "en" # default
        self.currency = "USD"
        self.validFrom = ""
        self.validThrough = ""
        self.eligibleRegions = ""

class BusinessEntity():
    """BusinessEntity class"""
    def __init__(self):
        self.id = ""
        self.type = ""
        self.legalName = ""
        self.street_address = ""
        self.postal_code = ""
        self.postal_box = ""
        self.location = ""
        self.region = ""
        self.country_name = ""
        self.tel = ""
        self.fax = ""
        self.email = ""
        self.page = ""

class Offer():
    """Offering class"""
    def __init__(self):
        self.id = ""
        self.description = ""
        self.comment = ""
        self.uom = "C62"
        self.price_quantity = "1.0" # amountOfThisGood
        self.validFrom = ""
        self.validThrough = ""
        self.price = ""
        self.price_factor = "1"
        self.currency = ""
        self.product_quantity = "" # eligibleQuantity min
        self.eligibleRegions = ""
        self.ean = ""
        self.manufacturer_id = ""
        self.taxes = 0

class Tag(): 
    """Class carrying tag metadata"""
    def __init__(self, stack, attrs, content):
        self.stack = stack
        self.attrs = attrs
        self.content = content
