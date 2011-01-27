#!/usr/bin/env python
"""serializer.py

Serializes arrays of classes as RDF/XML

Created by Alex Stolz on 2011-01-26
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
from globvars import *
from rdflib import *

owl = "http://www.w3.org/2002/07/owl#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
gr = "http://purl.org/goodrelations/v1#"
foaf = "http://xmlns.com/foaf/0.1/"
vcard = "http://www.w3.org/2006/vcard/ns#"
xsd = "http://www.w3.org/2001/XMLSchema#"
OWL = Namespace(owl)
RDFS = Namespace(rdfs)
GR = Namespace(gr)
FOAF = Namespace(foaf)
VCARD = Namespace(vcard)
XSD = Namespace(xsd)

g = Graph()
g.bind("owl", owl)
g.bind("rdfs", rdfs)
g.bind("gr", gr)
g.bind("foaf", foaf)
g.bind("vcard", vcard)
g.bind("xsd", xsd)

def triple(subject, predicate, object, datatype=None, language=None):
    """Create a triple in graph g"""
    if type(object) == Literal:
        # return if content is empty
        if object.title() == "":
            return
        # check if language tag is given
        if language != None:
            object.language = language
        # if no language tag is given, check if datatype is available
        elif datatype != None:
            object.datatype = datatype
    # create triple in graph g
    g.add((subject, predicate, object))

def serializeBusinessEntity(be):
    """Serialize a single business entity"""
    identifier = "".join(str(be.legalName).split()) # remove spaces
    lang = catalog.lang[:2] # make de out of deu
    
    # graph node uris
    be_about = URIRef("#be_"+identifier)
    be_address = URIRef("#address_"+identifier)
    
    # annotate graph
    triple(be_about, RDF.type, GR.BusinessEntity)
    triple(be_about, GR.legalName, Literal(be.legalName), language=lang)
    triple(be_about, GR.hasGlobalLocationNumber, Literal(be.gln), datatype=XSD.string)
    triple(be_about, GR.hasDUNS, Literal(be.duns), datatype=XSD.string)
    # vcard
    triple(be_about, VCARD.url, URIRef(be.page))
    triple(be_about, VCARD.email, Literal(be.email), datatype=XSD.string)
    triple(be_about, VCARD.tel, Literal(be.tel))
    triple(be_about, VCARD.fax, Literal(be.fax))
    triple(be_about, VCARD.fn, Literal(be.legalName), language=lang)
    # address
    triple(be_about, VCARD.adr, be_address)
    triple(be_address, RDF.type, VCARD.Address)
    triple(be_address, VCARD['street-address'], Literal(be.street_address), language=lang)
    triple(be_address, VCARD['postal-code'], Literal(be.postal_code), datatype=XSD.string)
    triple(be_address, VCARD['post-office-box'], Literal(be.postal_box), language=lang)
    triple(be_address, VCARD.locality, Literal(be.location), language=lang)
    triple(be_address, VCARD.region, Literal(be.region), language=lang)
    triple(be_address, VCARD['country-name'], Literal(be.country_name), language=lang)

    #print g.serialize(format="pretty-xml")
    
def serializeOffer(offer):
    """Serialize a single offering"""
    identifier = offer.id
    manufacturer_id = offer.manufacturer_id
    # use offer id as fallback identifier for manufacturer
    if manufacturer_id == "":
        manufacturer_id = identifier
    lang = catalog.lang[:2] # make de out of deu
    
    # graph node uris
    o_about = URIRef("#offer_"+identifier)
    o_taqn = URIRef("#taqn_"+identifier)
    o_product = URIRef("#product_"+identifier)
    o_model = URIRef("#model_"+identifier)
    o_price = URIRef("#price_"+identifier)
    o_quantity = URIRef("#quantity_"+identifier)
    o_manufacturer = URIRef("#manufacturer_"+manufacturer_id)
    
    # annotate graph
    # offer level
    triple(o_about, RDF.type, GR.Offering)
    triple(o_about, GR.description, Literal(offer.description), language=lang)
    triple(o_about, RDFS.comment, Literal(offer.comment), language=lang)
    triple(o_about, GR.validFrom, Literal(offer.validFrom), datatype=XSD.dateTime)
    triple(o_about, GR.validThrough, Literal(offer.validThrough), datatype=XSD.dateTime)
    triple(o_about, GR.eligibleRegions, Literal(offer.eligibleRegions), datatype=XSD.string) # TODO: check in what format eligibleRegions is passed!!
    triple(o_about, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
    triple(o_about, GR.hasEligibleQuantity, o_quantity)
    triple(o_quantity, RDF.type, GR.QuantitativeValueFloat)
    triple(o_quantity, GR.hasUnitOfMeasurement, Literal(offer.uom), datatype=XSD.string)
    triple(o_quantity, GR.hasMinValueFloat, Literal(offer.product_quantity), datatype=XSD.float)
    # TODO: hasBusinessFunction -> get from if supplier, buyer or party role was used
    # pricespecification level
    triple(o_about, GR.hasPriceSpecification, o_price)
    triple(o_price, RDF.type, GR.UnitPriceSpecification)
    triple(o_price, GR.validFrom, Literal(offer.validFrom), datatype=XSD.dateTime)
    triple(o_price, GR.validThrough, Literal(offer.validThrough), datatype=XSD.dateTime)
    triple(o_price, GR.hasUnitOfMeasurement, Literal(offer.uom), datatype=XSD.string)
    triple(o_price, GR.valueAddedTaxIncluded, Literal((offer.taxes>0)), datatype=XSD.boolean) # TODO: implement taxes
    triple(o_price, GR.hasCurrency, Literal(offer.currency), datatype=XSD.string)
    if offer.price and offer.price_factor:
        triple(o_price, GR.hasCurrencyValue, Literal(float(offer.price)*float(offer.price_factor)), datatype=XSD.float)
    # typeandquantitynode level
    triple(o_about, GR.includesObject, o_taqn)
    triple(o_taqn, RDF.type, GR.TypeAndQuantityNode)
    triple(o_taqn, GR.amountOfThisGood, Literal(offer.price_quantity), datatype=XSD.float)
    triple(o_taqn, GR.hasUnitOfMeasurement, Literal(offer.uom), datatype=XSD.string)
    # productorservice level
    triple(o_taqn, GR.typeOfGood, o_product)
    triple(o_product, RDF.type, GR.ProductOrServicesSomeInstancesPlaceholder)
    triple(o_product, GR.description, Literal(offer.description), language=lang)
    triple(o_product, RDFS.comment, Literal(offer.comment), language=lang)
    triple(o_product, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
    # productmodel level
    triple(o_product, GR.hasMakeAndModel, o_model)
    triple(o_model, RDF.type, GR.ProductOrServiceModel)
    triple(o_model, GR.description, Literal(offer.description), language=lang)
    triple(o_model, RDFS.comment, Literal(offer.comment), language=lang)
    triple(o_model, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
    # manufacturer level
    triple(o_model, GR.hasManufacturer, o_manufacturer)
    triple(o_manufacturer, RDF.type, GR.BusinessEntity)
    triple(o_manufacturer, GR.name, Literal(offer.manufacturer_name))
    
    
    #print g.serialize(format="pretty-xml")

def serialize():
    """Serialize array of objects"""
    global catalog, bes, offers
    
    # serialize objects
    for be in bes:
        serializeBusinessEntity(be)
        # debug output
        print "B: ", be.id, " -> ", be.legalName
    for offer in offers:
        serializeOffer(offer)
        # debug output
        print "O: ", offer.id, " -> ",  offer.description
        
    print g.serialize(format="pretty-xml")#format="pretty-xml")