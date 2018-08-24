import urllib.request, urllib.parse, json, datetime, re, io
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
endpoint = 'http://vocab.getty.edu/sparql.rdf?query='

# AAT entity construct statement beginning and end
construct_begin = """CONSTRUCT {
?s ?p1 ?o1.
?s dc:identifier ?o2.
?s skos:scopeNote ?o3.
?s skos:broader ?o4.
?s skos:hasTopConcept ?o5.
?s dcterms:created ?o6.
?s dcterms:modified ?mod1.
?s a ?t1
} WHERE {
BIND ( <http://vocab.getty.edu/aat/"""

construct_end = """> as ?s)
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
query_encode = urllib.parse.quote(topconcept_construct)
req = urllib.request.Request(url=endpoint+query_encode+end_url,headers={'Accept':'text/html'})
with urllib.request.urlopen(req) as response:
    the_page = response.read().decode()
    page_lines = the_page.splitlines()
    inDescription = False
    for line in page_lines:
        if 'rdf:Description' in line:
            if inDescription == True:
                print(line, file = outfile, end = '\n')
                inDescription = False
            else:
                inDescription = True
        if inDescription:
            print(line, file = outfile, end = '\n')
sparql = SPARQLWrapper("http://vocab.getty.edu/sparql")
sparql.setQuery("select * {?x skos:inScheme aat:}")
sparql.setReturnFormat(JSON)
d = sparql.query().convert()
for index in range(len(d['results']['bindings'])):
    uri=d['results']['bindings'][index]['x']['value']
    aat_id=uri.replace('http://vocab.getty.edu/aat/','')
    print(aat_id)
    query_encode = urllib.parse.quote(construct_begin+aat_id+construct_end)
    req = urllib.request.Request(url=endpoint+query_encode+end_url,headers={'Accept':'text/html'})
    with urllib.request.urlopen(req) as response:
        the_page = response.read().decode()
        page_lines = the_page.splitlines()
        inDescription = False
        for line in page_lines:
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
