import urllib.request, urllib.parse, json, datetime, re, io, requests
from SPARQLWrapper import SPARQLWrapper, JSON

# begin file and add prefixes
file_begin = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
	xmlns:skos="http://www.w3.org/2004/02/skos/core#"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:dct="http://purl.org/dc/terms/"
	xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
"""

file_end = '</rdf:RDF>'
# set SPARQL endpoint
endpoint = 'http://vocab.getty.edu/sparql'

# AAT entity construct statement beginning and end
construct_query = """CONSTRUCT {
?s ?p1 ?o1.
?s dc:identifier ?o2.
?s skos:scopeNote ?o3.
?s skos:broader ?o4.
?s skos:hasTopConcept ?o5.
?s dcterms:created ?o6.
?s dcterms:modified ?mod1.
?s a ?t1
} WHERE {
BIND ( <http://vocab.getty.edu/aat/ENTITY_ID> as ?s)
{?s ?p1 ?o1
FILTER(!isBlank(?o1) && (?p1=skos:prefLabel || ?p1=skos:altLabel))}
UNION {?s a ?t1 FILTER(?t1=skos:Concept || ?t1=skos:Collection)}
UNION {?s skos:scopeNote/rdf:value ?o3 FILTER(!isBlank(?o3))}
UNION {?s gvp:broaderPreferred ?o4}
UNION {?s gvp:broaderExtended ?o5. ?o5 a gvp:Facet}
UNION {?s dc:identifier ?o2}
UNION {?s dcterms:created ?o6}
UNION {select (max(?mod) as ?mod1) {?s dcterms:modified ?mod}}
}"""

# top concept (facet) contruct statement
topconcept_construct = """
CONSTRUCT {
aat: skos:hasTopConcept ?f.
aat: a ?t
} WHERE {?f a gvp:Facet; skos:inScheme aat:.
aat: a ?t
}
"""

# parameters needed for querying SPARQL endpoint using urllib
end_url = '&_implicit=false&implicit=true&_equivalent=false&_form=%2Fsparql'

outfile = open('AATSKOS_All.rdf','w',encoding='utf8')
print(file_begin, file = outfile, end = '\n')
the_page = requests.post(endpoint,data={'query':topconcept_construct},headers={'Accept':'application/rdf+xml','Accept-Charset':'utf-8'})
the_page.encoding='utf-8'
inDescription = False
for line in the_page.text.splitlines():
    if 'rdf:Description' in line:
        if inDescription == True:
            print(line, file = outfile, end = '\n')
            inDescription = False
        else:
            inDescription = True
    if inDescription:
        print(line, file = outfile, end = '\n')
sparql = SPARQLWrapper(endpoint)
sparql.setQuery("select * {?x skos:inScheme aat:}") # entire AAT
#sparql.setQuery("select * {?x gvp:broaderExtended aat:300053003}") # use this query for individual facets
sparql.setReturnFormat(JSON)
d = sparql.query().convert()
for index in range(len(d['results']['bindings'])):
    uri=d['results']['bindings'][index]['x']['value']
    aat_id=uri.replace('http://vocab.getty.edu/aat/','')
    print(aat_id)
    the_page = requests.post(endpoint,data={'query':construct_query.replace('ENTITY_ID',aat_id)},headers={'Accept':'application/rdf+xml','Accept-Charset':'utf-8'})
    the_page.encoding='utf-8'
    inDescription = False
    for line in the_page.text.splitlines():
        if 'rdf:Description' in line:
            if inDescription == True:
                print(line, file = outfile, end = '\n')
                inDescription = False
            else:
                inDescription = True
        if inDescription:
            print(line, file = outfile, end = '\n')
print(file_end, file = outfile, end = '\n')
outfile.close()
