

# Table of Contents #


# Introduction #

BMEcat2GoodRelations is a command line tool that allows providers of product data (manufacturers, retailers, PIM/SaaS providers) to lift datasheets and/or offers onto the Web of Linked Data. By that companies (e.g. manufacturers) can enhance the visibility of their products and are well prepared for imminent e-commerce tools. In addition, positive network externalities can be exploited because Web shops and search engines are likely to grasp these data for the provision of more detailed product information in their catalogs and search results. This, again, will emphasize the product's strengths and increase the demand.

To achieve this goal our script basically converts a product catalog available in standard BMEcat XML format to its GoodRelations counterpart. The tool is capable to handle both BMEcat 1.2 and BMEcat 2005 file formats. However, BMEcat 2005 is favorable due to undergone improvements compared to prior versions, for example the introduction of multi-language support.

# Usage #

In this section we propose a method for the configuration and the deployment of the tool that proved successful in practice.

Subsequently we assume a company "ACME" from which we know the following details:
  * BMEcat file: `bmecat_acme.xml`
  * Web site: `http://www.acme.com/`
  * Product page: `http://catalog.acme.com/products?artnr=ART_ID`
  * Image URI: `http://www.acme.com/images/products/ART_ID.jpg`
  * Preferred URI for deployment: `http://data.acme.com/`
  * Offered products have price information and are mass products (no individual products, i.e. a certain instance of a product sold only once)

## Getting Started ##

We start with a basic example. Though not yet very powerful, you could issue the following command to convert a BMEcat XML file named `bmecat_example.xml` to GoodRelations:
```
$ python main.py bmecat_acme.xml
```
Since neither output folder nor base URI for the deployment are specified, the tool will assume default values. More precisely, the converted files will be stored in a folder named "output" and the deployment URI is set to `http://www.example.com/data/`, which is going to be the location where the contents of "output" will be published when deployed.

To obtain more control over the output the script understands several option/argument-pairs that can be passed via the command line. The output destination can be indicated with the option `-o` or `--output=`. Likewise, the base URI for the deployment is specified using the `-b` or `--base=` option. The next two snippets detail both possibilities:
```
$ python main.py -o output -b http://data.acme.com/ bmecat_acme.xml
```
```
$ python main.py --output=output --base_uri=http://data.acme.com/ bmecat_acme.xml
```

Finally the command below provides a more comprehensive and powerful example. Besides the options for output and base URI also the path to the images and  a pattern for the product pages can be configured. The the former is optional and applies only to images with relative URIs, whereas the latter is highly recommended in order to establish links to the product detail pages that provide additional information about the products.
```
$ python main.py -o output -b http://data.acme.com/ -i http://www.acme.com/images/products/
-p "http://catalog.acme.com/products?artnr=%s" bmecat_acme.xml
```

## Command Line Options ##

```
$ python main.py --help
```

```
USAGE
python main.py [options] FILE

OPTIONS
-o <output>	customize location of output folder
		(default = output)
-b <base>	provide base uri for deployment
		(default = http://www.example.com/data/)
-l <language>	2-letter language code according to ISO 639-1
		(default = try to determine from catalog)
-t <type>	configure the type of product (if "model", then will print product model catalog only)
		(default = actual)
		Possible values are [1]:
		* actual: products are likely all gr:Individual, and
		* placeholder: products are likely all gr:SomeItems
		* model: only product model data (gr:ProductOrServiceModel) is considered, i.e. offer data is skipped
-i <url>	full url path to image folder that contains images as specified in bmecat file
		(default = ignore)
-p <pattern>	pattern for product page urls
		(default = "")
		product url pattern, any string containing %s is allowed, e.g. http://www.example.com/products/id_%s/
--help		print usage summary

[1] http://www.heppnetz.de/ontologies/goodrelations/v1#ProductOrService
```

| **abbreviation** | **example** | **alternative** | **example**|
|:-----------------|:------------|:----------------|:|
| -h | `-h` | --help | `--help` |
| -o | `-o output/` | --output= | `--output=output/` |
| -b | `-b http://data.acme.com/` | --base= | `--base=http://data.acme.com/` |
| -l | `-l de` | --language= | `--language=de` |
| -t | `-t actual` | --type= | `--type=actual` |
| -p | `-p "http://catalog.acme.com/products?artnr=A123"` | --pattern | `--pattern="http://catalog.acme.com/products?artnr=A123"` |
| -i | `-i http://www.acme.com/images/products/A123.jpg` | --image\_base= | `--image_base=http://www.acme.com/images/products/A123.jpg` |

## Deployment ##

Basically it is possible to do conversion and publication on two physically disparate machines. In practice, however, it seems most feasible to install both the script and a Cronjob on the host system to serve the publication folder periodically with the most up-to-date product data in GoodRelations. Depending on the frequency of data changes, this interval may vary from an hourly basis to once a week.

We imagine two possibilities come into question regarding the topology:
  * conversion and data deployment on one and the same host, or
  * conversion and deployment on separate systems, then file transfer of results between the two hosts (SFTP, SCP, etc.).

The execution of the conversion script could be prompted via:
  * the installation of a periodically recurring Cronjob task, or
  * events thrown as modifications to the contents in the PIM system are observed.

We suggest to use a dedicated server space to host the GoodRelations data. A subdomain like e.g. `http://data.example.com/` seems most appropriate, since the file structure therein will then look as follows:
```
http://data.example.com/sitemap.xml
http://data.example.com/dump/dump.nt.gz
http://data.example.com/rdf/cataloggroups.rdf
http://data.example.com/rdf/properties.rdf
http://data.example.com/rdf/product_XYZ001.rdf
http://data.example.com/rdf/product_XYZ124.rdf
...
```

## Linkage with Product Pages ##

If the article id/number can be found in the URI of the product detail page then it makes sense to provide a common URI pattern for all product detail pages. If supplied then each RDF file will contain a link to the corresponding HTML pages. The respective option is `-p` or `--pattern=`:
```
$ python main.py -o output -b http://data.acme.com/ -i http://www.acme.com/images/products/
-p "http://catalog.acme.com/products?artnr=%s" bmecat_acme.xml
```
The `%s` serves here as a placeholder for the article number. The outlined pattern would match any URI of the following form:
```
http://catalog.acme.com/products?artnr=%s (pattern)
http://catalog.acme.com/products?artnr=A123
http://catalog.acme.com/products?artnr=XYZ001
http://catalog.acme.com/products?artnr=90119991
```

Please note and be warned that the product URI pattern has to be embraced by quotes, otherwise the special characters will be wrongly recognized and interpreted by the shell.

## Images ##

Media objects are recognized automatically unless they use relative URIs. If this is the case, objects other than images will be quietly ignored. However, images with relative paths will be considered if the `-i`/`--image\_base='-option is set on the command line.
```
<MIME>
  <MIME_TYPE>image/jpeg</MIME_TYPE>
  <MIME_SOURCE>A123.jpg</MIME_SOURCE>
  <MIME_PURPOSE>normal</MIME_PURPOSE>
  <MIME_DESCR>Full-sized image</MIME_DESCR>
  <MIME_ALT>Product image for A123</MIME_ALT>
</MIME>
```

The image path `http://www.acme.com/images/products/` applied to the image `A123.jpg` will thus result in the product image URI `http://www.acme.com/images/products/A123.jpg`.

## Unit Code Mapping ##

The specification of BMEcat prescribes that unit codes should adhere to the UNCEFACT standard.
Since we observed during tool development that BMEcat files are often published with unit codes that do not conform to the UNCEFACT standard, we added support for the provision of a ";"-separted CSV file (named `uom.csv`) that contains a mapping between the proprietary unit codes and the corresponding UNCEFACT codes.
A typical mapping file has to comply with the following extract:
```
m;MTR;meter
mm;MMT;millimeter
mm&sup2;MMK;square millimeter
l;LTR;liter
g;GRM;gram
```
In the first column (until first occurrence of a semicolon) are listed the proprietary unit codes, the second column denotes the corresponding UNCEFACT codes and the third column is optional and can be used for short comments.
In the source code folder you'll find an example CSV file with possible mappings that we are shipping out of the box. It's aimed to serve as a basis and should be extended or replaced by own unit codes.

If the script finds and loads the `uom.csv` successfully then the following message should be printed somewhere at the beginning of the standard output: `Try to read UOM mapping from "uom.csv"... found and prepared UOM mapping`.

A thorough list of available UNCEFACT codes can be found [here (html table)](http://www.unece.org/cefact/recommendations/add2a.htm) or [here (pdf and xls files for download)](http://www.unece.org/cefact/recommendations/rec20en.htm).

## Robots.txt ##

To facilitate search engines the indexing process we recommend to provide a `robots.txt` file in the root directory of your server domain/subdomain that points to the sitemap file.
```
Sitemap: http://data.acme.com/sitemap.xml
```

# Advanced #

The tasks outlined in the next few subsections require a deeper understanding of latest Web technologies than those in the prior section. But they are definitely worth the effort.

## Use of Existing Classification Standards ##

This subsection may be skipped if you are not using a classification standard but rather your own product catalog. However, you may be interested in adding one of the standards around like e.g. eCl@ss.

The tool inherently supports eCl@ss 5.1 references for classes and properties. If you are aware of any other standard published on the Web, so you may extend the function(s) `getClassURI()` and `getPropertyURI()` in the file `config.py` on your own. You are invited to contact us if you need assistance ([Web page](http://www.ebusiness-unibw.org/)).

```
def getClassURI(system_id, group_id):
    """Returns the class URI of a given reference classification system, e.g. eClassOWL"""
    if not system_id or not group_id:
        return ""
    if system_id == "ECLASS-5.1":
        return "http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#C_"+group_id["value"]
    # add additional classification system classes here
    else:
        return ""
    
def getPropertyURI(system_id, fref):
    """Returns the property URI of a given reference classification system, e.g. eClassOWL"""
    if not system_id or not fref:
        return ""
    if system_id == "ECLASS-5.1":
        return "http://www.ebusiness-unibw.org/ontologies/eclass/5.1.4/#P_"+fref
    # add additional classification system properties here
    else:
        return ""
```

## Embedding RDFa in HTML Pages ##

### DOCTYPE ###

The DOCTYPE of the HTML page should be modified for each page that is going to contain RDFa snippets. The following listing shows an example for RDFa in XHTML.
```
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.0//EN" "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" version="XHTML+RDFa 1.0" xml:lang="##proper language code, e.g. de##">
```
A quick introduction to RDFa in HTML is given in the [GoodRelations Quickstart Guide](http://wiki.goodrelations-vocabulary.org/Quickstart).

### Main Page, Imprint or Contact Page ###

It's straightforward to model the company details in place where the contact information can be found.

#### HTML Head ####

```
<head>
  ...
  <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8"/>
  <link rel="meta" type="application/rdf+xml" title="RDF/XML data for ACME"
    href="http://data.acme.com/rdf/company.rdf" />
  ...
</head>
```

#### At Some Place in the HTML Body ####

```
<div xmlns="http://www.w3.org/1999/xhtml" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:gr="http://purl.org/goodrelations/v1#" xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:vcard="http://www.w3.org/2006/vcard/ns#">
  <div typeof="gr:BusinessEntity" about="http://data.acme.com/rdf/company.rdf#be_ACME">
    <div property="gr:legalName" content="ACME"></div>
    <div property="vcard:tel" content="+49 111111111"></div>
    <div rel="vcard:adr">
      <div typeof="vcard:Address">
        <div property="vcard:country-name" content="Germany"></div>
        <div property="vcard:locality" content="Munich, Neubiberg"></div>
        <div property="vcard:postal-code" content="85579"></div>
        <div property="vcard:street-address" content="Werner-Heisenberg-Weg 39"></div>
      </div>
    </div>
    <div rel="foaf:logo" resource="http://www.acme.com/images/ci_logo_acme.jpg"></div>
    <div rel="foaf:page" resource=""></div>
  </div>
</div>
```

### Product Detail Page ###

Each product detail page should mention a subset of the full information as found in the corresponding RDF/XML file. Google currently honors if at least gr:name and price information (gr:UnitPriceSpecification) for a gr:Offering are available.

#### HTML Head ####

```
<head>
  ...
  <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8"/>
  <link rel="meta" type="application/rdf+xml" title="RDF/XML data for product ##ARTNR##"
    href="http://data.acme.com/rdf/product_##article number##.rdf" />
  ...
</head>
```

#### At Some Place in the HTML Body ####

```
<div xmlns="http://www.w3.org/1999/xhtml" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema#" xmlns:gr="http://purl.org/goodrelations/v1#"
  xmlns:foaf="http://xmlns.com/foaf/0.1/">
  <div typeof="gr:Offering" about="http://data.acme.com/rdf/product_##article number##.rdf#offer">
    <div rev="gr:offers" resource="http://data.acme.com/rdf/company.rdf#be_ACME"></div>
    <div property="gr:name" content="##product name##" xml:lang="##proper language code, e.g. de##"></div>
    <div property="gr:description" content="##product description##" xml:lang="##proper language code, e.g. de##"></div>
    <div property="gr:hasEAN_UCC-13" content="##ean code##" datatype="xsd:string"></div>
    <div rel="gr:hasBusinessFunction" resource="http://purl.org/goodrelations/v1#Sell"></div>
    <div rel="gr:hasPriceSpecification">
      <div typeof="gr:UnitPriceSpecification">
        <div property="gr:hasCurrency" content="EUR" datatype="xsd:string"></div>
        <div property="gr:hasCurrencyValue" content="389.45" datatype="xsd:float"></div>
        <div property="gr:hasUnitOfMeasurement" content="C62" datatype="xsd:string"></div>
      </div>
    </div>
    <div rel="foaf:page" resource="http://catalog.acme.com/products?artnr=##article number##"></div>
  </div>
</div>
```
Replace:
  * URIs by your own URIs
  * patterns by corresponding values

### Testing with Google Rich Snippets ###

We encourage you to test your newly created RDFa pages with the _Google Rich Snippet Testing Tool_ in order to ensure your snippet will appear in the search engine search results:

http://www.google.com/webmasters/tools/richsnippets

## HTTP Redirects and Content Negotiation ##

Redirect browser requests on RDF/XML files to their corresponding product page URI using an `.htaccess`-file (on Apache HTTP server):
```
RewriteCond %{HTTP_ACCEPT} !application/rdf\+xml.*(text/html|application/xhtml\+xml)
RewriteCond %{HTTP_ACCEPT} text/html [OR]
RewriteCond %{HTTP_ACCEPT} application/xhtml\+xml [OR]
RewriteCond %{HTTP_USER_AGENT} ^Mozilla/.*
RewriteRule product_(.+)\.rdf http://catalog.acme.com/products?artnr=([$1]) [R=303]
```
The above snippet makes sure that any request by a Browser or a User Agent that prefers HTML over RDF/XML is redirected to the corresponding information source.

tbd:
Optimize content negotiation for correct delivery of RDF/XML and XHTML+RDFa.

## The Pro Solution ##

tbd:
more structure (make sure to separate UOM from values in properties) eases reuse and reduces computational complexity and effort for consumers