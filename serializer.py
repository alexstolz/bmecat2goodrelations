#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import gzip

from util import *

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
    def __init__(self, output_folder="", base_uri="", catalog=None, lang="", image_uri="", model_only=False, pattern=""):
        """Initialization"""

        self.be_about = None
        self.lang = lang
        self.catalog = catalog
        self.base_uri = base_uri
        self.output_folder = output_folder
        self.image_uri = image_uri
        self.model_only = model_only
        self.pattern = pattern
        
        self.offerfile_id = "offer"
        if self.model_only:
            self.offerfile_id = "model"
        self.feature_graph = Graph()
        self.feature_graph.bind("owl", owl)
        while len(self.output_folder)>0 and self.output_folder[-1] == "/": # remove trailing slashes
            self.output_folder = self.output_folder[:-1]
        while len(self.base_uri)>0 and self.base_uri[-1] == "/":
            self.base_uri = self.base_uri[:-1]
        while len(self.image_uri)>0 and self.image_uri[-1] == "/":
            self.image_uri = self.image_uri[:-1]
            
        # try mkdir output folder
        #if not os.path.exists(self.output_folder):
        try:
            os.makedirs(self.output_folder+"/dump")
            os.makedirs(self.output_folder+"/rdf")
        except OSError:
            pass
        
        # serialize objects
        self.dump = gzip.open(output_folder+"/dump/dump.nt.gz", "wb")
        self.feature_file = open(output_folder+"/rdf/features.rdf", "w")
        self.sitemap = open(output_folder+"/sitemap.xml", "w")
        self.sitemap.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:sc=\"http://sw.deri.org/2007/07/sitemapextension/scschema.xsd\">\n")
            
    def __del__(self):
        """Destruction"""
        self.sitemap.write("</urlset>")
        self.feature_file.write(self.feature_graph.serialize(format="pretty-xml"))
        self.dump.write(self.feature_graph.serialize(format="nt"))
        
    def store(self, object, object_type):
        """Write serialization variants to files"""
        if object_type == "offer":
            file = open("%s/rdf/%s_%s.rdf" % (self.output_folder, self.offerfile_id, object.id), "w")
            file.write(self.serializeOffer(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeOffer(object, rdf_format="nt"))
            """
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Metadata for product %(offer)s \"%(objectid)s\"</sc:datasetLabel>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">%(baseuri)s/rdf/%(offer)s_%(objectid)s.rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>%(baseuri)s/rdf/%(offer)s_%(objectid)s.rdf#offer</sc:sampleURI>\n\
        <sc:dataDumpLocation>%(baseuri)s/rdf/%(offer)s_%(objectid)s.rdf</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n" % ({"offer":self.offerfile_id, "objectid":object.id, "baseuri":self.base_uri}))
            """
            
        elif object_type == "be":
            import datetime
            file = open(self.output_folder+"/rdf/company.rdf", "w")
            file.write(self.serializeBusinessEntity(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeBusinessEntity(object, rdf_format="nt"))
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Semantic Web dataset of %(legalname)s</sc:datasetLabel>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">%(baseuri)s/</sc:linkedDataPrefix>\n\
        <sc:dataDumpLocation>%(baseuri)s/dump/dump.nt.gz</sc:dataDumpLocation>\n\
        <lastmod>%(lastmod)s</lastmod>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n" % ({"baseuri":self.base_uri, "legalname":object.legalName, "lastmod":datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%SZ")}))
            """
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Company Metadata</sc:datasetLabel>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">%(baseuri)s/rdf/company.rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>%(baseuri)s/rdf/company.rdf#be_%(legalname)s</sc:sampleURI>\n\
        <sc:dataDumpLocation>%(baseuri)s/rdf/company.rdf</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n" % ({"baseuri":self.base_uri, "legalname":re.sub(r"[^a-zA-Z0-9]", "", "".join(str(object.legalName).split()))}))
            print "wrote company %s" % object.legalName
            """
            
        elif object_type == "catalog":
            file = open(self.output_folder+"/rdf/catalog.rdf", "w")
            file.write(self.serializeCatalogStructure(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeCatalogStructure(object, rdf_format="nt"))
            """
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>BMECat Catalog Structure</sc:datasetLabel>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">%(baseuri)s/rdf/catalog.rdf#</sc:linkedDataPrefix>\n\
        <sc:dataDumpLocation>%(baseuri)s/rdf/catalog.rdf</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n" % ({"baseuri":self.base_uri}))
            print "wrote catalog"
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Proprietary Property Catalog Structure</sc:datasetLabel>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">%(baseuri)s/rdf/features.rdf#</sc:linkedDataPrefix>\n\
        <sc:dataDumpLocation>%(baseuri)s/rdf/features.rdf</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n" % ({"baseuri":self.base_uri}))
            print "wrote features"
            """
        
    
    def triple(self, g, subject, predicate, object, datatype=None, language=None):
        """Create a triple in graph g"""
        if None in [subject, predicate, object]: # NoneType object, don't create triple
            return
        elif type(object) == Literal:
            # return if content is empty
            if object.title() == "":
                return
            # check if language tag is given
            if language != None:
                object.language = language
            # if no language tag is given, check if datatype is available
            elif datatype != None:
                object.datatype = datatype
        elif type(object) == URIRef:
            if object.title() == "":
                return
        else: # neither Literal nor URIRef
            print "WARNING: triple(%s, %s, %s) not created - object type neither Literal nor URIRef" % (str(subject), str(predicate), str(object))
            return
        # create triple in graph g
        g.add((subject, predicate, object))
        
    def serializeCatalogStructure(self, catalog_hierarchy, rdf_format):
        """Serialize the catalog"""
        g = Graph()
        g.bind("owl", owl)
        g.bind("foaf", foaf)
        
        selfns = self.base_uri+"/rdf/catalog.rdf#C_"
        g.bind("self", selfns)
        lang = mapLanguage(self.catalog.lang)
        if self.lang:
            lang = self.lang
        
        for catalog_group in catalog_hierarchy:
            id = catalog_group.id
            if not id:
                continue # skip if no id available
            parent_id = catalog_group.parent_id
            parent_idref_tax = None
            if parent_id:
                parent_idref_tax = URIRef(selfns+parent_id+"-tax")
            idref_tax = URIRef(selfns+id+"-tax")
            idref_gen = URIRef(selfns+id+"-gen") # gen has no hierarchy, hence no parent id for gen classes
            
            # tax
            self.triple(g, idref_tax, RDF.type, OWL.Class)
            self.triple(g, idref_tax, RDFS.subClassOf, parent_idref_tax)
            label_tax = ""
            if catalog_group.name != "":
                label_tax = catalog_group.name+" (Taxonomy Concept: Anything that may be an instance of this category in any context)"
            else:
                label_tax = "(Taxonomy Concept: Anything that may be an instance of this category in any context)"
            self.triple(g, idref_tax, RDFS.label, Literal(label_tax), language=lang)
            self.triple(g, idref_tax, RDFS.comment, Literal(catalog_group.description), language=lang)
            # media
            self.appendMedia(g, idref_tax, catalog_group)
            
            # gen
            self.triple(g, idref_gen, RDF.type, OWL.Class)
            self.triple(g, idref_gen, RDFS.subClassOf, GR.ProductOrService)
            self.triple(g, idref_gen, RDFS.subClassOf, idref_tax)
            label_gen = ""
            if catalog_group.name != "":
                label_gen = catalog_group.name+" (Generic Concept: This type of goods)"
            else:
                label_gen = "(Generic Concept: This type of goods)"
            self.triple(g, idref_gen, RDFS.label, Literal(label_gen), language=lang)
            self.triple(g, idref_gen, RDFS.comment, Literal(catalog_group.description), language=lang)
            # media
            self.appendMedia(g, idref_gen, catalog_group)
            
        return g.serialize(format=rdf_format)
            
    def serializeBusinessEntity(self, be, rdf_format):
        """Serialize a single business entity"""
        g = Graph()
        g.bind("owl", owl)
        g.bind("gr", gr)
        g.bind("foaf", foaf)
        g.bind("vcard", vcard)
        
        identifier = re.sub(r"[^a-zA-Z0-9]", "", "".join(str(be.legalName).split())) # remove spaces
        selfns = self.base_uri+"/rdf/company.rdf#"
        g.bind("self", selfns)
        lang = mapLanguage(self.catalog.lang) # make de out of deu
        if self.lang: # command line
            lang = self.lang
        
        # graph node uris
        be_about = URIRef(selfns+"be_"+identifier)
        self.be_about = be_about
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
        
        # media
        self.appendMedia(g, be_about, be)
    
        return g.serialize(format=rdf_format)
        
    def serializeOffer(self, offer, rdf_format):
        """Serialize a single offering"""
        g = Graph()
        g.bind("owl", owl)
        g.bind("gr", gr)
        g.bind("cat", self.base_uri+"/rdf/catalog.rdf#")
        g.bind("prop", self.base_uri+"/rdf/features.rdf#")
        g.bind("foaf", foaf)
        
        selfns = self.base_uri+"/rdf/"+self.offerfile_id+"_"+offer.id+".rdf#"
        g.bind("self", selfns)
        manufacturer_id = offer.manufacturer_id
        # use offer id as fallback identifier for manufacturer
        if manufacturer_id == "":
            manufacturer_id = offer.id
        lang = mapLanguage(self.catalog.lang) # make de out of deu
        if self.lang: # command line
            lang = self.lang
        
        # create product url for foaf:page links
        product_url = createProductURI(offer.id, self.pattern)
        
        # graph node uris
        o_about = URIRef(selfns+"offer")
        o_taqn = URIRef(selfns+"taqn")
        o_product = URIRef(selfns+"product")
        o_model = URIRef(selfns+"model")
        o_price = URIRef(selfns+"price")
        o_quantity = URIRef(selfns+"order_quantity")
        p_quantity = URIRef(selfns+"price_quantity")
        o_manufacturer = URIRef(selfns+"manufacturer_"+manufacturer_id)
        
        # annotate graph
        if not self.model_only:
            # offer level
            self.triple(g, self.be_about, GR.offers, o_about)
            self.triple(g, o_about, RDF.type, GR.Offering)
            self.triple(g, o_about, GR.name, Literal(offer.description), language=lang)
            self.triple(g, o_about, GR.description, Literal(offer.comment), language=lang)
            if offer.validFrom:
                self.triple(g, o_about, GR.validFrom, Literal(convert2datetime(offer.validFrom)), datatype=XSD.dateTime)
            else: # global validFrom
                self.triple(g, o_about, GR.validFrom, Literal(convert2datetime(self.catalog.validFrom)), datatype=XSD.dateTime)
            if offer.validThrough:
                self.triple(g, o_about, GR.validThrough, Literal(convert2datetime(offer.validThrough)), datatype=XSD.dateTime)
            else: # global validThrough
                self.triple(g, o_about, GR.validThrough, Literal(convert2datetime(self.catalog.validThrough)), datatype=XSD.dateTime)
            for region in set(offer.eligibleRegions) | set(self.catalog.eligibleRegions):
                self.triple(g, o_about, GR.eligibleRegions, Literal(region), datatype=XSD.string)
            self.triple(g, o_about, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
            self.triple(g, o_about, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
            self.triple(g, o_about, GR.hasMPN, Literal(offer.mpn), datatype=XSD.string)
            self.triple(g, o_about, GR.condition, Literal(offer.condition))
            if offer.order_uom and offer.order_units:
                self.triple(g, o_about, GR.hasEligibleQuantity, o_quantity)
                self.triple(g, o_quantity, RDF.type, GR.QuantitativeValueFloat)
                self.triple(g, o_quantity, GR.hasUnitOfMeasurement, Literal(offer.order_uom), datatype=XSD.string)
                self.triple(g, o_quantity, GR.hasValueFloat, Literal(offer.order_units), datatype=XSD.float)
            # hasBusinessFunction
            self.triple(g, o_about, GR.hasBusinessFunction, GR.Sell)
            self.triple(g, o_about, FOAF.page, URIRef(product_url))
            # pricespecification level
            if offer.price and (offer.currency or self.catalog.currency):
                self.triple(g, o_about, GR.hasPriceSpecification, o_price)
                self.triple(g, o_price, RDF.type, GR.UnitPriceSpecification)
                if offer.order_uom and offer.price_lower:
                    self.triple(g, o_price, GR.hasEligibleQuantity, p_quantity)
                    self.triple(g, p_quantity, RDF.type, GR.QuantitativeValueFloat)
                    self.triple(g, p_quantity, GR.hasUnitOfMeasurement, Literal(offer.order_uom), datatype=XSD.string)
                    self.triple(g, p_quantity, GR.hasMinValueFloat, Literal(offer.price_lower), datatype=XSD.float)
                self.triple(g, o_price, GR.validFrom, Literal(convert2datetime(offer.validFrom)), datatype=XSD.dateTime)
                self.triple(g, o_price, GR.validThrough, Literal(convert2datetime(offer.validThrough)), datatype=XSD.dateTime)
                self.triple(g, o_price, GR.hasUnitOfMeasurement, Literal(offer.order_uom), datatype=XSD.string)
                self.triple(g, o_price, GR.valueAddedTaxIncluded, Literal(offer.taxes), datatype=XSD.boolean)
                if offer.currency:
                    self.triple(g, o_price, GR.hasCurrency, Literal(offer.currency), datatype=XSD.string)
                else: # global currency
                    self.triple(g, o_price, GR.hasCurrency, Literal(self.catalog.currency), datatype=XSD.string)
                if offer.price and offer.price_factor:
                    self.triple(g, o_price, GR.hasCurrencyValue, Literal(float(offer.price)*float(offer.price_factor)), datatype=XSD.float)
            # media
            self.appendMedia(g, o_about, offer)
            # typeandquantitynode level
            self.triple(g, o_about, GR.includesObject, o_taqn)
            self.triple(g, o_taqn, RDF.type, GR.TypeAndQuantityNode)
            self.triple(g, o_taqn, GR.amountOfThisGood, Literal(offer.content_units), datatype=XSD.float)
            self.triple(g, o_taqn, GR.hasUnitOfMeasurement, Literal(offer.content_uom), datatype=XSD.string)
            # productorservice level
            self.triple(g, o_taqn, GR.typeOfGood, o_product)
            if self.catalog.typeOfProducts == "actual":
                self.triple(g, o_product, RDF.type, GR.ActualProductOrServiceInstance)
            else:
                self.triple(g, o_product, RDF.type, GR.ProductOrServicesSomeInstancesPlaceholder)
            self.triple(g, o_product, GR.name, Literal(offer.description), language=lang)
            self.triple(g, o_product, GR.description, Literal(offer.comment), language=lang)
            self.triple(g, o_product, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
            self.triple(g, o_product, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
            self.triple(g, o_product, GR.hasMPN, Literal(offer.mpn), datatype=XSD.string)
            self.triple(g, o_product, GR.condition, Literal(offer.condition))
            self.triple(g, o_product, FOAF.page, URIRef(product_url))
            # media
            self.appendMedia(g, o_product, offer)
            # productmodel level
            self.triple(g, o_product, GR.hasMakeAndModel, o_model)
        self.triple(g, o_model, RDF.type, GR.ProductOrServiceModel)
        self.triple(g, o_model, GR.name, Literal(offer.description), language=lang)
        self.triple(g, o_model, GR.description, Literal(offer.comment), language=lang)
        self.triple(g, o_model, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
        self.triple(g, o_model, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
        self.triple(g, o_model, GR.hasMPN, Literal(offer.mpn), datatype=XSD.string)
        self.triple(g, o_model, GR.condition, Literal(offer.condition))
        self.triple(g, o_model, FOAF.page, URIRef(product_url))
        # media
        self.appendMedia(g, o_model, offer)
        # manufacturer level
        self.triple(g, o_model, GR.hasManufacturer, o_manufacturer)
        self.triple(g, o_manufacturer, RDF.type, GR.BusinessEntity)
        self.triple(g, o_manufacturer, GR.name, Literal(offer.manufacturer_name))
        # product feature classes
        for product_feature in offer.product_features:
            system_id = product_feature.reference_feature_system_name
            if product_feature.reference_feature_system_id: # system_id should be same as system_name, hence overwrite if available
                system_id = product_feature.reference_feature_system_id
            # create gr:category
            if product_feature.reference_feature_group_name != "":
                if system_id:
                    category_string = product_feature.reference_feature_group_name+" (%s)" % system_id
                self.triple(g, o_product, GR.category, Literal(category_string), language=lang)
                self.triple(g, o_model, GR.category, Literal(category_string), language=lang)
            # class uris
            if product_feature.reference_feature_group_id["value"] != "" and product_feature.reference_feature_group_id["type"] == "flat":
                classURI = getClassURI(system_id, product_feature.reference_feature_group_id)
                self.triple(g, o_product, RDF.type, URIRef(classURI))
                self.triple(g, o_model, RDF.type, URIRef(classURI))
            if product_feature.reference_feature_group_id2["value"] != "" and product_feature.reference_feature_group_id2["type"] == "flat":
                classURI = getClassURI(system_id, product_feature.reference_feature_group_id2)
                self.triple(g, o_product, RDF.type, URIRef(classURI))
                self.triple(g, o_model, RDF.type, URIRef(classURI))
            # feature classes
            for feature in product_feature.features:
                # determine whether qualitative or quantitative
                qualitative = False
                if feature.unit == "":
                    qualitative = True
                fidentifier = re.sub(r"[^a-zA-Z0-9]", "", "".join(feature.name.split()))
                feature_id = URIRef(selfns+fidentifier)
                
                feature_prop_idref = re.sub(r"[^a-zA-Z0-9]", "", "".join(str(system_id+"_"+fidentifier).split()))
                # try get property from existing reference ontology
                fref_property = getPropertyURI(system_id, feature.fref)
                if fref_property:
                    feature_prop_id = URIRef(fref_property)
                else: # else create a custom property
                    feature_prop_id = URIRef(self.base_uri+"/rdf/features.rdf#P_"+system_id+"_"+fidentifier)
                    # create suitable object property
                    self.triple(self.feature_graph, feature_prop_id, RDF.type, OWL.ObjectProperty) # prop_id for external access
                    if qualitative:
                        self.triple(self.feature_graph, feature_prop_id, RDFS.label, Literal("Property %s (%s)" % (fidentifier, system_id)), language="en")
                        self.triple(self.feature_graph, feature_prop_id, RDFS.comment, Literal("\"%s\" property according to \"%s\" classification." % (fidentifier, system_id)), language="en")
                        self.triple(self.feature_graph, feature_prop_id, RDFS.subPropertyOf, GR.qualitativeProductOrServiceProperty)
                        self.triple(self.feature_graph, feature_prop_id, RDFS.range, GR.QualitativeValue)
                    else:
                        self.triple(self.feature_graph, feature_prop_id, RDFS.label, Literal("Property %s (%s)" % (fidentifier, system_id)), language="en")
                        self.triple(self.feature_graph, feature_prop_id, RDFS.comment, Literal("\"%s\" property according to \"%s\" classification." % (fidentifier, system_id)), language="en")
                        self.triple(self.feature_graph, feature_prop_id, RDFS.subPropertyOf, GR.quantitativeProductOrServiceProperty)
                        self.triple(self.feature_graph, feature_prop_id, RDFS.range, GR.QuantitativeValueFloat)
                    self.triple(self.feature_graph, feature_prop_id, RDFS.domain, GR.ProductOrService)
                
                self.triple(g, o_model, feature_prop_id, feature_id)
                if qualitative:
                    self.triple(g, feature_id, RDF.type, GR.QualitativeValue)
                else:
                    self.triple(g, feature_id, RDF.type, GR.QuantitativeValueFloat)
                    self.triple(g, feature_id, GR.hasUnitOfMeasurement, Literal(feature.unit), datatype=XSD.string)
                    self.triple(g, feature_id, GR.hasValueFloat, Literal(feature.value), datatype=XSD.float)
                unit = ""
                if feature.unit:
                    unit = " "+feature.unit # nicer formatting
                self.triple(g, feature_id, GR.name, Literal("%s is %s%s" % (feature.name, feature.value, unit)), language="en")
                if unit:
                    self.triple(g, feature_id, GR.description, Literal("The product has a \"%s\" of \"%s%s\"." % (feature.name, feature.value, unit)), language="en")
                else:
                    self.triple(g, feature_id, GR.description, Literal("The \"%s\" of the product is \"%s\"." % (feature.name, feature.value)), language="en")
        # catalog
        for cataloggroup_id in offer.cataloggroup_ids:
            # make productorservice...instance and productorservicemodel instances of gen classes
            if not self.model_only:
                self.triple(g, o_product, RDF.type, URIRef(self.base_uri+"/rdf/catalog.rdf#C_"+cataloggroup_id+"-gen"))
            self.triple(g, o_model, RDF.type, URIRef(self.base_uri+"/rdf/catalog.rdf#C_"+cataloggroup_id+"-gen"))
        
        return g.serialize(format=rdf_format)
    
    def appendMedia(self, g, subject, entity):
        """attach media information to graph"""
        for mime in entity.media:
            if self.image_uri != "ignore" and re.match(r"image", mime.type): # image/png, ...
                if re.match(r"^http://", mime.source):
                    self.triple(g, subject, FOAF.depiction, URIRef(mime.source))
                elif re.match(r"^http://", self.image_uri):
                    item = mime.source
                    while len(item)>0 and item[0]=="/": # remove leading slashes in item
                        item = item[1:]
                    self.triple(g, subject, FOAF.depiction, URIRef(self.image_uri+"/"+item))
            else:
                if(re.match(r"^http://", mime.source)):
                    self.triple(g, subject, RDFS.seeAlso, URIRef(mime.source))
    
    