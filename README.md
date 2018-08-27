# AAT SKOS Extract for OpenTheso

This script extracts all AAT records from the Getty Vocabularies LOD site in the SKOS format for import in the [OpenTheso](https://github.com/miledrousset/opentheso) thesaurus management tool. The tool expects a RDF/XML serialized version of the data. The script produces the current version of AAT available at: http://vocab.getty.edu

## Requirements

The script was built and run using Python 3.6.5. Package dependencies:

JSON\
SPARQLWrapper\
urllib\
datetime\
re\
io

## Output

The script produces the file AAT_SKOS.rdf in the same directory where the script is located. A recently generated copy of AAT_SKOS.rdf is provided in this repo.
