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
import datetime

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
    def __init__(self, output_folder="", base_uri="", catalog=None, lang=""):
        """Initialization"""
        self.lang = lang
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
        if object_type == "offer":
            file = open(self.output_folder+"/offer_"+object.id+".rdf", "w")
            file.write(self.serializeOffer(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeOffer(object, rdf_format="nt"))
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Offering Metadata for product offer \""+object.id+"\"</sc:datasetLabel>\n\
        <sc:datasetURI>"+self.base_uri+"offer_"+object.id+".rdf</sc:datasetURI>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">"+self.base_uri+"offer_"+object.id+".rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>"+self.base_uri+"offer_"+object.id+".rdf#offer</sc:sampleURI>\n\
        <sc:dataDumpLocation>"+self.base_uri+"dump.nt</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n")
            
        elif object_type == "be":
            file = open(self.output_folder+"/company.rdf", "w")
            file.write(self.serializeBusinessEntity(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeBusinessEntity(object, rdf_format="nt"))
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>Company Metadata</sc:datasetLabel>\n\
        <sc:datasetURI>"+self.base_uri+"company.rdf</sc:datasetURI>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">"+self.base_uri+"company.rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>"+self.base_uri+"company.rdf#be_"+re.sub(r"[^a-zA-Z0-9]", "", "".join(str(object.legalName).split()))+"</sc:sampleURI>\n\
        <sc:dataDumpLocation>"+self.base_uri+"dump.nt</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n")
            print "wrote", "(company)", object.legalName
            
        elif object_type == "catalog":
            file = open(self.output_folder+"/catalog.rdf", "w")
            file.write(self.serializeCatalogStructure(object, rdf_format="pretty-xml"))
            self.dump.write(self.serializeCatalogStructure(object, rdf_format="nt"))
            self.sitemap.write("    <sc:dataset>\n\
        <sc:datasetLabel>BMECat Catalog Structure</sc:datasetLabel>\n\
        <sc:datasetURI>"+self.base_uri+"catalog.rdf</sc:datasetURI>\n\
        <sc:linkedDataPrefix slicing=\"subject-object\">"+self.base_uri+"catalog.rdf#</sc:linkedDataPrefix>\n\
        <sc:sampleURI>"+self.base_uri+"catalog.rdf#be_</sc:sampleURI>\n\
        <sc:dataDumpLocation>"+self.base_uri+"dump.nt</sc:dataDumpLocation>\n\
        <changefreq>weekly</changefreq>\n\
    </sc:dataset>\n")
        
    
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
        elif type(object) == URIRef:
            if object.title() == "":
                return
        # create triple in graph g
        g.add((subject, predicate, object))
        
    def serializeCatalogStructure(self, catalog_hierarchy, rdf_format):
        """Serialize the catalog"""
        g = Graph()
        g.bind("owl", owl)
        
        selfns = self.base_uri+"catalog.rdf#"
        g.bind("self", selfns)
        lang = self.mapLanguage(self.catalog.lang)
        if self.lang:
            lang = self.lang
        
        for catalog_group in catalog_hierarchy:
            id = re.sub(r"[^a-zA-Z0-9]", "", catalog_group.id)
            parent_id = re.sub(r"[^a-zA-Z0-9]", "", catalog_group.parent_id)
            idref_tax = URIRef(selfns+id+"_tax")
            parent_idref_tax = URIRef(selfns+parent_id+"_tax")
            idref_gen = URIRef(selfns+id+"_gen") # gen has no hierarchy, hence no parent id for gen classes
            
            # tax
            self.triple(g, idref_tax, RDF.type, OWL.Class)
            self.triple(g, idref_tax, RDFS.subClassOf, parent_idref_tax)
            label_tax = ""
            if catalog_group.name != "":
                label_tax = catalog_group.name+" [Taxonomy Concept: Anything that may be an instance of this category in any context]"
            else:
                label_tax = "[Taxonomy Concept: Anything that may be an instance of this category in any context]"
            self.triple(g, idref_tax, RDFS.label, Literal(label_tax), language=lang)
            self.triple(g, idref_tax, RDFS.comment, Literal(catalog_group.description), language=lang)
            # gen
            self.triple(g, idref_gen, RDFS.type, OWL.Class)
            self.triple(g, idref_gen, RDFS.subClassOf, GR.ProductOrService)
            self.triple(g, idref_gen, RDFS.subClassOf, idref_tax)
            label_gen = ""
            if catalog_group.name != "":
                label_gen = catalog_group.name+" [Generic Concept: This type of goods]"
            else:
                label_gen = "[Generic Concept: This type of goods]"
            self.triple(g, idref_gen, RDFS.label, Literal(label_gen), language=lang)
            self.triple(g, idref_gen, RDFS.comment, Literal(catalog_group.description), language=lang)
            
        return g.serialize(format=rdf_format)
            
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
        lang = self.mapLanguage(self.catalog.lang) # make de out of deu
        if self.lang: # command line
            lang = self.lang
        
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
        
    def serializeOffer(self, offer, rdf_format):
        """Serialize a single offering"""
        g = Graph()
        g.bind("owl", owl)
        g.bind("gr", gr)
        g.bind("cat", self.base_uri+"catalog.rdf#")
        
        identifier = re.sub(r"[^a-zA-Z0-9]", "", offer.id)
        selfns = self.base_uri+"offer_"+identifier+".rdf#"
        g.bind("self", selfns)
        manufacturer_id = re.sub(r"[^a-zA-Z0-9]", "", offer.manufacturer_id)
        # use offer id as fallback identifier for manufacturer
        if manufacturer_id == "":
            manufacturer_id = identifier
        lang = self.mapLanguage(self.catalog.lang) # make de out of deu
        if self.lang: # command line
            lang = self.lang
        
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
        # offer level
        self.triple(g, o_about, RDF.type, GR.Offering)
        self.triple(g, o_about, GR.name, Literal(offer.description), language=lang)
        self.triple(g, o_about, GR.description, Literal(offer.comment), language=lang)
        if offer.validFrom:
            self.triple(g, o_about, GR.validFrom, Literal(self.convert2datetime(offer.validFrom)), datatype=XSD.dateTime)
        else: # global validFrom
            self.triple(g, o_about, GR.validFrom, Literal(self.convert2datetime(self.catalog.validFrom)), datatype=XSD.dateTime)
        if offer.validThrough:
            self.triple(g, o_about, GR.validThrough, Literal(self.convert2datetime(offer.validThrough)), datatype=XSD.dateTime)
        else: # global validThrough
            self.triple(g, o_about, GR.validThrough, Literal(self.convert2datetime(self.catalog.validThrough)), datatype=XSD.dateTime)
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
            self.triple(g, o_quantity, GR.hasMinValueFloat, Literal(offer.order_units), datatype=XSD.float)
        # hasBusinessFunction
        self.triple(g, o_about, GR.hasBusinessFunction, GR.Sell)
        # pricespecification level
        self.triple(g, o_about, GR.hasPriceSpecification, o_price)
        self.triple(g, o_price, RDF.type, GR.UnitPriceSpecification)
        if offer.order_uom and offer.price_lower:
            self.triple(g, o_price, GR.hasEligibleQuantity, p_quantity)
            self.triple(g, p_quantity, RDF.type, GR.QuantitativeValueFloat)
            self.triple(g, p_quantity, GR.hasUnitOfMeasurement, Literal(offer.order_uom), datatype=XSD.string)
            self.triple(g, p_quantity, GR.hasMinValueFloat, Literal(offer.price_lower), datatype=XSD.float)
        self.triple(g, o_price, GR.validFrom, Literal(self.convert2datetime(offer.validFrom)), datatype=XSD.dateTime)
        self.triple(g, o_price, GR.validThrough, Literal(self.convert2datetime(offer.validThrough)), datatype=XSD.dateTime)
        self.triple(g, o_price, GR.hasUnitOfMeasurement, Literal(offer.order_uom), datatype=XSD.string)
        self.triple(g, o_price, GR.valueAddedTaxIncluded, Literal(offer.taxes), datatype=XSD.boolean)
        if offer.currency:
            self.triple(g, o_price, GR.hasCurrency, Literal(offer.currency), datatype=XSD.string)
        else: # global currency
            self.triple(g, o_price, GR.hasCurrency, Literal(self.catalog.currency), datatype=XSD.string)
        if offer.price and offer.price_factor:
            self.triple(g, o_price, GR.hasCurrencyValue, Literal(float(offer.price)*float(offer.price_factor)), datatype=XSD.float)
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
        # productmodel level
        self.triple(g, o_product, GR.hasMakeAndModel, o_model)
        self.triple(g, o_model, RDF.type, GR.ProductOrServiceModel)
        self.triple(g, o_model, GR.name, Literal(offer.description), language=lang)
        self.triple(g, o_model, GR.description, Literal(offer.comment), language=lang)
        self.triple(g, o_model, GR['hasEAN_UCC-13'], Literal(offer.ean), datatype=XSD.string)
        self.triple(g, o_model, GR['hasGTIN-14'], Literal(offer.gtin), datatype=XSD.string)
        self.triple(g, o_model, GR.hasMPN, Literal(offer.mpn), datatype=XSD.string)
        self.triple(g, o_model, GR.condition, Literal(offer.condition))
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
            self.triple(g, feature_prop_id, RDF.type, OWL.ObjectProperty)
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
            self.triple(g, feature_id, GR.name, Literal(feature.name+" is "+feature.value), language="en")
            self.triple(g, feature_id, GR.description, Literal("The product feature _"+feature.name+"_ has the value _"+feature.value+feature.unit+"_"), language="en")
        # catalog
        for cataloggroup_id in offer.cataloggroup_ids:
            # make productorservice...instance and productorservicemodel instances of gen classes
            self.triple(g, o_product, RDF.type, URIRef(self.base_uri+"catalog.rdf#"+cataloggroup_id+"_gen"))
            self.triple(g, o_model, RDF.type, URIRef(self.base_uri+"catalog.rdf#"+cataloggroup_id+"_gen"))
        
        return g.serialize(format=rdf_format)
    
    def convert2datetime(self, datestring):
        if re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", datestring):
            mydatetime = datetime.datetime.strptime(datestring, "%Y-%m-%d")
            return mydatetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            return ""
    
    def mapLanguage(self, iso639_2):
        """language mappings iso639_2 -> iso639_1"""
        mappings = {
            "aar":"aa",
            "abk":"ab",
            "afr":"af",
            "aka":"ak",
            "alb":"sq", "sqi":"sq",
            "amh":"am",
            "ara":"ar",
            "arg":"an",
            "arm":"hy", "hye":"hy",
            "asm":"as",
            "ava":"av",
            "ave":"ae",
            "aym":"ay",
            "aze":"az",
            "bak":"ba",
            "bam":"bm",
            "baq":"eu", "eus":"eu",
            "bel":"be",
            "ben":"bn",
            "bih":"bh",
            "bis":"bi",
            "tib":"bo", "bod":"bo",
            "bos":"bs",
            "bre":"br",
            "bul":"bg",
            "bur":"my", "mya":"my",
            "cat":"ca",
            "cze":"cs", "ces":"cs",
            "cha":"ch",
            "che":"ce",
            "chi":"zh", "zho":"zh",
            "chu":"cu",
            "chv":"cv",
            "cor":"kw",
            "cos":"co",
            "cre":"cr",
            "wel":"cy", "cym":"cy",
            "dan":"da",
            "ger":"de", "deu":"de",
            "div":"dv",
            "dut":"nl", "nld":"nl",
            "dzo":"dz",
            "gre":"el", "ell":"el",
            "eng":"en",
            "epo":"eo",
            "est":"et",
            "ewe":"ee",
            "fao":"fo",
            "per":"fa", "fas":"fa",
            "fij":"fj",
            "fin":"fi",
            "fre":"fr", "fra":"fr",
            "fry":"fy",
            "ful":"ff",
            "geo":"ka", "kat":"ka",
            "gla":"gd",
            "gle":"ga",
            "glg":"gl",
            "glv":"gv",
            "grn":"gn",
            "guj":"gu",
            "hat":"ht",
            "hau":"ha",
            "heb":"he",
            "her":"hz",
            "hin":"hi",
            "hmo":"ho",
            "hrv":"hr",
            "hun":"hu",
            "ibo":"ig",
            "ice":"is", "isl":"is",
            "ido":"io",
            "iii":"ii",
            "iku":"iu",
            "ile":"ie",
            "ina":"ia",
            "ind":"id",
            "ipk":"ik",
            "ita":"it",
            "jav":"jv",
            "jpn":"ja",
            "kal":"kl",
            "kan":"kn",
            "kas":"ks",
            "geo":"ka", "kat":"ka",
            "kau":"kr",
            "kaz":"kk",
            "khm":"km",
            "kik":"ki",
            "kin":"rw",
            "kir":"ky",
            "kom":"kv",
            "kon":"kg",
            "kor":"ko",
            "kua":"kj",
            "kur":"ku",
            "lao":"lo",
            "lat":"la",
            "lav":"lv",
            "lim":"li",
            "lin":"ln",
            "lit":"lt",
            "ltz":"lb",
            "lub":"lu",
            "lug":"lg",
            "mac":"mk", "mkd":"mk",
            "mah":"mh",
            "mal":"ml",
            "mao":"mi", "mri":"mi",
            "mar":"mr",
            "may":"ms", "msa":"ms",
            "mac":"mk", "mkd":"mk",
            "mlg":"mg",
            "mlt":"mt",
            "mao":"mi", "mri":"mi",
            "may":"ms", "msa":"ms",
            "nau":"na",
            "nav":"nv",
            "nbl":"nr",
            "nde":"nd",
            "ndo":"ng",
            "nep":"ne",
            "nno":"nn",
            "nob":"nb",
            "nor":"no",
            "nya":"ny",
            "oci":"oc",
            "oji":"oj",
            "ori":"or",
            "orm":"om",
            "oss":"os",
            "pan":"pa",
            "pli":"pi",
            "pol":"pl",
            "por":"pt",
            "pus":"ps",
            "que":"qu",
            "roh":"rm",
            "rum":"ro", "ron":"ro",
            "run":"rn",
            "rus":"ru",
            "sag":"sg",
            "san":"sa",
            "sin":"si",
            "slo":"sk", "slk":"sk",
            "slv":"sl",
            "sme":"se",
            "smo":"sm",
            "sna":"sn",
            "snd":"sd",
            "som":"so",
            "sot":"st",
            "spa":"es",
            "srd":"sc",
            "srp":"sr",
            "ssw":"ss",
            "sun":"su",
            "swa":"sw",
            "swe":"sv",
            "tah":"ty",
            "tam":"ta",
            "tat":"tt",
            "tel":"te",
            "tgk":"tg",
            "tgl":"tl",
            "tha":"th",
            "tir":"ti",
            "ton":"to",
            "tsn":"tn",
            "tso":"ts",
            "tuk":"tk",
            "tur":"tr",
            "twi":"tw",
            "uig":"ug",
            "ukr":"uk",
            "urd":"ur",
            "uzb":"uz",
            "ven":"ve",
            "vie":"vi",
            "vol":"vo",
            "wln":"wa",
            "wol":"wo",
            "xho":"xh",
            "yid":"yi",
            "yor":"yo",
            "zha":"za",
            "zul":"zu"
            }
        iso639_2 = iso639_2.lower() # make lower case
        if len(iso639_2) == 2:
            iso639_1 = iso639_2
        elif iso639_2 in mappings.keys():
            iso639_1 = mappings[iso639_2]
        else:
            iso639_1 = "en" #default
        return iso639_1
    
        