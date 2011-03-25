#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""serializer.py

Serializes arrays of classes as RDF/XML

Created by Alex Stolz on 2011-03-25
Copyright (c) 2011 Universitaet der Bundeswehr. All rights reserved.

Author: Alex Stolz
Organization: E-Business and Web Science Research Group
"""
import re
import datetime

def getClassURI(system_id, group_id):
    """Returns the class URI of a given reference classification system, e.g. eClassOWL"""
    if not system_id or not group_id:
        return ""
    if system_id == "ECLASS-5.1":
        return "http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#C_"+group_id["value"]
    # add other ontology classes here
    else:
        return ""
    
def getPropertyURI(system_id, fref):
    """Returns the property URI of a given reference classification system, e.g. eClassOWL"""
    if not system_id or not fref:
        return ""
    if system_id == "ECLASS-5.1":
        return "http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#P_"+fref
    # add other ontology properties here
    else:
        return ""

def convert2datetime(datestring):
    """Convert a datestring formatted as yyyy-mm-dd to iso datetime format"""
    if re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", datestring):
        mydatetime = datetime.datetime.strptime(datestring, "%Y-%m-%d")
        return mydatetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        return ""
    
def mapLanguage(iso639_2):
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
