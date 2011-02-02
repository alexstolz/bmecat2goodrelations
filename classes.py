#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""classes.py

Defines classes

Created by Alex Stolz on 2011-01-26
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
class Catalog():
    """Catalog settings"""
    def __init__(self):
        self.lang = "en" # default
        self.currency = "USD"
        self.validFrom = ""
        self.validThrough = ""
        self.eligibleRegions = []
        
class CatalogGroup():
    """Catalog group class"""
    def __init__(self):
        self.id = ""
        self.parent_id = ""
        self.name = ""

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
        self.duns = ""
        self.gln = ""
        self.offers = [] # will contain all offering ids of be

class Offer():
    """Offering class"""
    def __init__(self):
        self.id = ""
        self.description = ""
        self.comment = ""
        self.content_uom = "C62" # uom, e.g. pen CONTENT_UNIT -> TypeAndQuantityNode.hasUnitOfMeasurement
        self.content_units = "1.0" # number of content units in order, e.g. 5 pens in 1 package NO_CU_PER_OU -> TypeAndQuantityNode.amountOfThisGood
        self.order_uom = "C62" # uom, e.g. package ORDER_UNIT -> Offering.hasEligibleQuantity.QuantitativeValueFloat.hasUnitOfMeasurement
        self.order_units = "1.0" # minimum number of packages per order, e.g. 2 packages QUANTITY_MIN -> Offering.hasEligibleQuantity.QuantitativeValueFloat.hasMinValueFloat
        self.price_lower = "1" # graduated prices LOWER_BOUND (unit is ORDER_UNIT) -> UnitPriceSpecification.hasEligibleQuantity
        self.validFrom = ""
        self.validThrough = ""
        self.price = ""
        self.price_factor = "1"
        self.currency = ""
        self.product_quantity = "" # eligibleQuantity min
        self.eligibleRegions = []
        self.ean = ""
        self.gtin = ""
        self.mpn = "" # manufacturer part number
        self.condition = "" # new, used, ...
        self.manufacturer_id = ""
        self.manufacturer_name = ""
        self.taxes = "true"
        self.features = [] # array of feature classes
        
class Feature():
    """Class for product features"""
    def __init__(self):
        self.name = ""
        self.value = ""
        self.unit = "" # if no unit given, then a qualitativevalueproperty, else quantitativevalueproperty

class Tag(): 
    """Class carrying tag metadata"""
    def __init__(self, stack, attrs, content):
        self.stack = stack
        self.attrs = attrs
        self.content = content
