#!/usr/bin/env python
"""serializer.py

Serializes arrays of classes as RDF/XML

Created by Alex Stolz on 2011-01-26
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
from rdflib import *
import os
import re

# namespaces
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

class Serializer:
    """Serializer class"""
    def __init__(self, output_folder="", base_uri="", catalog=None):
        """Initialization"""
        self.catalog = catalog
        self.base_uri = base_uri
        self.output_folder = output_folder
        while self.output_folder[-1] == "/": # remove trailing slashes
            self.output_folder = self.output_folder[:-1]
        if self.base_uri[-1] != "/":
            self.base_uri = self.base_uri + "/"
            
        # try mkdir output folder
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
            except OSError:
                pass
        
        # serialize objects
        self.dump = open(output_folder+"/dump.nt", "w")
        self.sitemap = open(output_folder+"/sitemap.xml", "w")
        self.sitemap.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:sc=\"http://sw.deri.org/2007/07/sitemapextension/scschema.xsd\">\n")
            
    def __del__(self):
        """Destruction"""
        self.sitemap.write("</urlset>")
        
    def store(self, object, object_type):
        """Write serialization variants to files"""
        self.be_supplier = None
        
        if object_type == "offer":
            file = open(self.output_folder+"/offer_"+object.id+".rdf", "w")
            file.write(self.serializeOffer(object, self.be_supplier, rdf_format="pretty-xml"))
            self.dump.write(self.serializeOffer(object, self.be_supplier, rdf_format="nt"))
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Offering Metadata for product offer \""+object.id+"\"</sc:datasetLabel>\n\
        <sc:datasetURI>"+self.base_uri+"offer_"+object.id+".rdf</sc:datasetURI>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">"+self.base_uri+"offer_"+object.id+".rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>"+self.base_uri+"offer_"+object.id+".rdf#offer</sc:sampleURI>\n\
        <sc:dataDumpLocation>"+self.base_uri+"dump.rdf</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n")
            print "wrote", "(offer)", object.description
            # TODO: write id into array, later append to business entity..
            
        elif object_type == "be":
            if object.type == "supplier": # supplier offers the offerings
                self.be_supplier = object
            file = open(self.output_folder+"/company.rdf", "w")
            file.write(self.serializeBusinessEntity(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeBusinessEntity(object, rdf_format="nt"))
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Company Metadata</sc:datasetLabel>\n\
        <sc:datasetURI>"+self.base_uri+"company.rdf</sc:datasetURI>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">"+self.base_uri+"company.rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>"+self.base_uri+"company.rdf#be_"+re.sub(r"[^a-zA-Z0-9]", "", "".join(str(object.legalName).split()))+"</sc:sampleURI>\n\
        <sc:dataDumpLocation>"+self.base_uri+"dump.rdf</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n")
            print "wrote", "(company)", object.legalName
        
    
    def triple(self, g, subject, predicate, object, datatype=None, language=None):
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
    
    def serializeBusinessEntity(self, be, rdf_format):
        """Serialize a single business entity"""
        g = Graph()
        g.bind("owl", owl)
        g.bind("gr", gr)
        g.bind("foaf", foaf)
        g.bind("vcard", vcard)
        
        identifier = re.sub(r"[^a-zA-Z0-9]", "", "".join(str(be.legalName).split())) # remove spaces
        selfns = self.base_uri+"company.rdf#"
        g.bind("self", selfns)
        lang = self.catalog.lang[:2] # make de out of deu
        
        # graph node uris
        be_about = URIRef(selfns+"be_"+identifier)
        be_address = URIRef(selfns+"address_"+identifier)
        
        # annotate graph
        self.triple(g, be_about, RDF.type, GR.BusinessEntity)
        self.triple(g, be_about, GR.legalName, Literal(be.legalName), language=lang)
        self.triple(g, be_about, GR.hasGlobalLocationNumber, Literal(be.gln), datatype=XSD.string)
        self.triple(g, be_about, GR.hasDUNS, Literal(be.duns), datatype=XSD.string)
        # vcard
        self.triple(g, be_about, VCARD.url, URIRef(be.page))
        self.triple(g, be_about, VCARD.email, Literal(be.email), datatype=XSD.string)
        self.triple(g, be_about, VCARD.tel, Literal(be.tel))
        self.triple(g, be_about, VCARD.fax, Literal(be.fax))
        self.triple(g, be_about, VCARD.fn, Literal(be.legalName), language=lang)
        # address
        self.triple(g, be_about, VCARD.adr, be_address)
        self.triple(g, be_address, RDF.type, VCARD.Address)
        self.triple(g, be_address, VCARD['street-address'], Literal(be.street_address), language=lang)
        self.triple(g, be_address, VCARD['postal-code'], Literal(be.postal_code), datatype=XSD.string)
        self.triple(g, be_address, VCARD['post-office-box'], Literal(be.postal_box), language=lang)
        self.triple(g, be_address, VCARD.locality, Literal(be.location), language=lang)
        self.triple(g, be_address, VCARD.region, Literal(be.region), language=lang)
        self.triple(g, be_address, VCARD['country-name'], Literal(be.country_name), language=lang)
        
        for offer_id in be.offers:
            ident = re.sub(r"[^a-zA-Z0-9]", "", offer_id)
            item = self.base_uri+"offer_"+ident+".rdf#"+"offer"
            self.triple(g, be_about, GR.offers, URIRef(item))
    
        return g.serialize(format=rdf_format)
        
    def serializeOffer(self, offer, be_supplier, rdf_format):
        """Serialize a single offering"""
        g = Graph()
        g.bind("owl", owl)
        g.bind("gr", gr)
        
        identifier = re.sub(r"[^a-zA-Z0-9]", "", offer.id)
        selfns = self.base_uri+"offer_"+identifier+".rdf#"
        g.bind("self", selfns)
        manufacturer_id = offer.manufacturer_id
        # use offer id as fallback identifier for manufacturer
        if manufacturer_id == "":
            manufacturer_id = identifier
        lang = self.catalog.lang[:2] # make de out of deu
        
        # graph node uris
        o_about = URIRef(selfns+"offer")
        o_taqn = URIRef(selfns+"taqn")
        o_product = URIRef(selfns+"product")
        o_model = URIRef(selfns+"model")
        o_price = URIRef(selfns+"price")
        o_quantity = URIRef(selfns+"quantity")
        o_manufacturer = URIRef(selfns+"manufacturer_"+manufacturer_id)
        
        # annotate graph
        # linkage with business entity
        if self.be_supplier:
            beidentifier = re.sub(r"[^a-zA-Z0-9]", "", "".join(str(self.be_supplier.legalName).split()))
            self.triple(g, URIRef(selfns+"be_"+beidentifier), GR.offers, o_about)
        # offer level
        self.triple(g, o_about, RDF.type, GR.Offering)
        self.triple(g, o_about, GR.description, Literal(offer.description), language=lang)
        self.triple(g, o_about, RDFS.comment, Literal(offer.comment), language=lang)
        if offer.validFrom:
            self.triple(g, o_about, GR.validFrom, Literal(offer.validFrom), datatype=XSD.dateTime)
        else: # global validFrom
            self.triple(g, o_about, GR.validFrom, Literal(self.catalog.validFrom), datatype=XSD.dateTime)
        if offer.validThrough:
            self.triple(g, o_about, GR.validThrough, Literal(offer.validThrough), datatype=XSD.dateTime)
        else: # global validThrough
            self.triple(g, o_about, GR.validThrough, Literal(self.catalog.validThrough), datatype=XSD.dateTime)
        self.triple(g, o_about, GR.eligibleRegions, Literal(offer.eligibleRegions), datatype=XSD.string) # TODO: check in what format eligibleRegions is passed!!
        if offer.eligibleRegions != self.catalog.eligibleRegions: # global eligibleRegions
            self.triple(g, o_about, GR.eligibleRegions, Literal(self.catalog.eligibleRegions), datatype=XSD.string)
        self.triple(g, o_about, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
        self.triple(g, o_about, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
        self.triple(g, o_about, GR.hasEligibleQuantity, o_quantity)
        self.triple(g, o_quantity, RDF.type, GR.QuantitativeValueFloat)
        self.triple(g, o_quantity, GR.hasUnitOfMeasurement, Literal(offer.uom), datatype=XSD.string)
        self.triple(g, o_quantity, GR.hasMinValueFloat, Literal(offer.product_quantity), datatype=XSD.float)
        # TODO: hasBusinessFunction -> get from if supplier, buyer or party role was used
        if self.be_supplier and self.be_supplier.type == "buyer":
            self.triple(g, o_about, GR.hasBusinessFunction, GR.Buy)
        else:
            self.triple(g, o_about, GR.hasBusinessFunction, GR.Sell)
        # pricespecification level
        self.triple(g, o_about, GR.hasPriceSpecification, o_price)
        self.triple(g, o_price, RDF.type, GR.UnitPriceSpecification)
        self.triple(g, o_price, GR.validFrom, Literal(offer.validFrom), datatype=XSD.dateTime)
        self.triple(g, o_price, GR.validThrough, Literal(offer.validThrough), datatype=XSD.dateTime)
        self.triple(g, o_price, GR.hasUnitOfMeasurement, Literal(offer.uom), datatype=XSD.string)
        self.triple(g, o_price, GR.valueAddedTaxIncluded, Literal((offer.taxes>0)), datatype=XSD.boolean) # TODO: implement taxes
        if offer.currency:
            self.triple(g, o_price, GR.hasCurrency, Literal(offer.currency), datatype=XSD.string)
        else: # global currency
            self.triple(g, o_price, GR.hasCurrency, Literal(self.catalog.currency), datatype=XSD.string)
        if offer.price and offer.price_factor:
            self.triple(g, o_price, GR.hasCurrencyValue, Literal(float(offer.price)*float(offer.price_factor)), datatype=XSD.float)
        # typeandquantitynode level
        self.triple(g, o_about, GR.includesObject, o_taqn)
        self.triple(g, o_taqn, RDF.type, GR.TypeAndQuantityNode)
        self.triple(g, o_taqn, GR.amountOfThisGood, Literal(offer.price_quantity), datatype=XSD.float)
        self.triple(g, o_taqn, GR.hasUnitOfMeasurement, Literal(offer.uom), datatype=XSD.string)
        # productorservice level
        self.triple(g, o_taqn, GR.typeOfGood, o_product)
        self.triple(g, o_product, RDF.type, GR.ProductOrServicesSomeInstancesPlaceholder)
        self.triple(g, o_product, GR.name, Literal(offer.description), language=lang)
        self.triple(g, o_product, GR.description, Literal(offer.comment), language=lang)
        self.triple(g, o_product, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
        self.triple(g, o_product, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
        # productmodel level
        self.triple(g, o_product, GR.hasMakeAndModel, o_model)
        self.triple(g, o_model, RDF.type, GR.ProductOrServiceModel)
        self.triple(g, o_model, GR.description, Literal(offer.description), language=lang)
        self.triple(g, o_model, RDFS.comment, Literal(offer.comment), language=lang)
        self.triple(g, o_model, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
        self.triple(g, o_model, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
        # manufacturer level
        self.triple(g, o_model, GR.hasManufacturer, o_manufacturer)
        self.triple(g, o_manufacturer, RDF.type, GR.BusinessEntity)
        self.triple(g, o_manufacturer, GR.name, Literal(offer.manufacturer_name))
        # features
        for feature in offer.features:
            # determine whether qualitative or quantitative
            qualitative = False
            if feature.unit == "":
                qualitative = True
            fidentifier = re.sub(r"[^a-zA-Z0-9]", "", "".join(feature.name.split()))
            feature_prop_id = URIRef(selfns+"prop_"+fidentifier)
            feature_id = URIRef(selfns+fidentifier)
            # create suitable object property
            self.triple(g, feature_prop_id, RDF.type, URIRef(OWL.ObjectProperty))
            if qualitative:
                self.triple(g, feature_prop_id, RDFS.subPropertyOf, GR.qualitativeProductOrServiceProperty)
                self.triple(g, feature_prop_id, RDFS.range, GR.QualitativeValue)
            else:
                self.triple(g, feature_prop_id, RDFS.subPropertyOf, GR.quantitativeProductOrServiceProperty)
                self.triple(g, feature_prop_id, RDFS.range, GR.QuantitativeValueFloat)
            self.triple(g, feature_prop_id, RDFS.domain, GR.ProductOrService)
            
            self.triple(g, o_model, feature_prop_id, feature_id)
            if qualitative:
                self.triple(g, feature_id, RDF.type, GR.QualitativeValue)
            else:
                self.triple(g, feature_id, RDF.type, GR.QuantitativeValueFloat)
                self.triple(g, feature_id, GR.hasUnitOfMeasurement, Literal(feature.unit), datatype=XSD.string)
                self.triple(g, feature_id, GR.hasMinValueFloat, Literal(feature.value), datatype=XSD.float)
            self.triple(g, feature_id, GR.name, Literal(feature.name+" "+feature.value), language="en")
            self.triple(g, feature_id, GR.description, Literal("The product feature _"+feature.name+"_ has got the value _"+feature.value+"_"), language="en")
        
        return g.serialize(format=rdf_format)
    
        