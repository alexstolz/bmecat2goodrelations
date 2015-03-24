


---


  * [>> Download](http://code.google.com/p/bmecat2goodrelations/downloads/list)
  * [>> User's Guide](Usage.md): Configuration and deployment instructions


---


## About ##

This portable command line tool aims at facilitating the generation of GoodRelations documents to large or medium-sized enterprises that already support the BMEcat format (e.g. via PIM systems). The resulting output is intended for a quick and efficient publication of highly structured offers on a Web scale.

## Features ##

The converter script consumes a BMEcat 2005 document (also downwards compatible with BMEcat 1.2) and creates a bunch of small documents including GoodRelations data. The script creates
  * a sitemap file,
  * a gzipped dump file (N-Triples) incorporating the whole data set,
  * an offer/model file for each single offering,
  * a data file including all defined product features, and
  * if available, a data file describing the full proprietary catalog structure and an HTML representation thereof.

The prerequisites to run the script are:
  * Python 2.X interpreter (at least 2.5 is desirable) [download page](http://www.python.org/getit/)
  * RDFLib 3.X (3.0 or 3.1) [download page](http://www.rdflib.net/)
  * Jinja2 templating engine [download and installation](http://jinja.pocoo.org/docs/intro/#installation)

Other features:
  * **Permissiveness and completeness.** The converter is tolerant with regard to unexpected input, i.e. it does not break on corrupted files with elements that appear at positions other than intended for. There are basically two versions of BMEcat in circulation, BMEcat 1.2 and BMEcat 2005. The differences between the two releases are manageable, most updates concern enhancements of the standard. Probably the most notable change was the renaming of any occurrence of ARTICLE to PRODUCT. The converter is able to deal with both versions and accepts even a mixture of them. Furthermore, BMEcat2005 introduced multi-language support which is also regarded appropriately by our tool.
  * **Extensibility.** Provided a group identifier and a base URI for a specific classification standard it is possible to establish the linkage to externally defined classes and properties. In the current version, this functionality is already built-in for eCl@ss 5.1.4, using its RDF representation provided by eClassOWL.
  * **User-friendliness and standards-compliance.** The converter script is invoked from command-line, where it provides usage instructions. The tool affords an opportunity to select whether to reveal the transactional data (in particular, details like price information or delivery options) or to keep them private. If the latter option is chosen the tool will only produce product model data instead of complete offering descriptions.

In addition to that, the HTML output that is produced in conjunction with the catalog group system serves as a navigable document to discover the class hierarchy the product models belong to. If published online together with all other files, the human-readable document allows to dereference the categories of the product models that were assigned to them, and this way helps to explore the context and thus to disambiguate product models more easily.

## Quickstart ##

The basic usage of the command line tool is as follows:
```
python main.py [options] FILE
```
You'll get a pretty nice summary of the possible options if you issue the following command:
```
python main.py --help
```

## Requirements ##

When executing on a Windows platform, the application will supposably create the most important files but will probably fail during the final process of HTML file creation. This issue is due to compabtibility problems of RDFLib with Windows, hence you have to replace RDFLib's original parser modules with the parser.py provided in the download section.

## Publications ##

**Alex Stolz, Bene Rodriguez-Castro, and Martin Hepp:** [Using BMEcat Catalogs as a Lever for Product Master Data on the Semantic Web](http://eswc-conferences.org/sites/default/files/papers2013/stolz.pdf). Proceedings of the [10th Extended Semantic Web Conference (ESWC 2013)](http://2013.eswc-conferences.org/), (Montpellier, France, 2013). ([slides](http://www.stalsoft.com/presentations/bmecat2goodrelations-eswc2013-talk.pdf))

## License and Source Code ##

The source code distributed via this Google repository is available under a free LGPL license.

## Acknowledgements ##

BMEcat2GoodRelations is available under the terms of the GNU Lesser General Public License. The work on this project has been supported by the [German Federal Ministry of Education and Research (BMBF)](http://www.bmbf.de/en/) by a grant under the KMU Innovativ program as part of the [Intelligent Match project](http://www.intelligent-match.de/) (FKZ 01IS10022B).

[![](http://www.productontology.org/static/bmbf.png)](http://www.bmbf.de/en/)