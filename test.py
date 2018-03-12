# fsm.py - http://www.graphviz.org/content/fsm

from graphviz import Digraph
import rdflib


f = Digraph('hierarchie', filename='visualisation.gv')
f.attr(rankdir='LR', size='8,5')

def createClass (nameClass,parentName):
    f.attr('node', shape='circle')
    f.edge(nameClass,parentName,'rdf:subClassOf')


def createInstance (nameInstance,className):
    f.attr('node', shape='circle')
    f.node(className)
    f.attr('node', shape='box')
    f.edge(nameInstance,className,'rdf:type')

def createRelation (relationRange,domain,relationName):
    f.attr('node', shape='box')
    f.node(relationRange)
    f.node(domain)
    f.edge(relationRange,domain,relationName)



g=rdflib.Graph()
g.load('ontology-rdf.owl')

individues = g.query(
    """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?sub ?type
    WHERE {
        ?sub rdf:type ?type.
        ?sub a ?class.
      FILTER( ?class = owl:NamedIndividual).
      FILTER (?type != owl:NamedIndividual)
    }""")

instances = []
classes = []
classesNames = []
properties = []
propertiesEffective = []

me = False

for row in individues:
    if(len(row[0].split("#"))>1 and len(row[1].split("#"))>1):
        instance = row[0].split("#")[1]
        className = row[1].split("#")[1]

        instances.append((instance,className))
        if me==False:
            me = row[1].split("#")[0]

        test = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX me: <"""+me+"""#>
        SELECT ?class
        WHERE {
            me:"""+className+""" rdfs:subClassOf ?class.
        }"""

        #print test

        newClassesMere = g.query(test)

        if className not in classesNames:
            classesNames.append(className)

        for motherClass in newClassesMere:
            if(len(motherClass[0].split("#"))>1):
                motherClassName = motherClass[0].split("#")[1]
                if((className,motherClassName) not in classes):
                    classes.append((className,motherClassName))

                if motherClassName not in classesNames:
                    classesNames.append(motherClassName)


for classe in classes:
    className = classe[1]
    test = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX me: <"""+me+"""#>
    SELECT ?class
    WHERE {
        me:"""+className+""" rdfs:subClassOf ?class.
    }"""

    newClassesMere = g.query(test)

    for motherClass in newClassesMere:
        if(len(motherClass[0].split("#"))>1):
            motherClassName = motherClass[0].split("#")[1]
            if((className,motherClassName) not in classes):
                classes.append((className,motherClassName))

            if motherClassName not in classesNames:
                classesNames.append(className)

for className in classesNames:

    propertiesQuery = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX me: <"""+me+"""#>
    SELECT DISTINCT ?p ?r ?d
    WHERE {
    {?p rdfs:range me:"""+className+"""} UNION {?p rdfs:domain me:"""+className+"""}.
    ?p rdfs:range ?r.
    ?p rdfs:domain ?d.
    }"""

    rows = g.query(propertiesQuery)

    for row in rows:
        if(len(row[0].split("#"))>1):
            propertyName = row[0].split("#")[1]
        if(len(row[0].split("#"))>1):
            rangeName = row[1].split("#")[1]
        if(len(row[0].split("#"))>1):
            domainName = row[2].split("#")[1]
        newRow = (propertyName, rangeName, domainName)

        if newRow not in properties:
            properties.append(newRow)


for prop in properties:
    propertiesQuery= """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX me: <"""+me+"""#>    SELECT  ?d ?r
    WHERE
    {
	?d me:"""+prop+"""?r.
    }
    """

    print (propertiesQuery)

    rows = g.query(propertiesQuery)

    for row in rows:
        if(len(row[0].split("#"))>1):
            domainInstance = row[0].split("#")[1]
        if(len(row[0].split("#"))>1):
            rangeInstance = row[1].split("#")[1]
        newRow = (domainInstance,rangeInstance,prop)

        if newRow not in propertiesEffective:
            propertiesEffective.append(newRow)


for classe in instances:
    createInstance(classe[0],classe[1])
    #print "%s instance of %s" %(classe[0],classe[1])

for prop in properties:
    #print "prop:%s range:%s dom:%s" %(prop[0],prop[1],prop[2])
    createRelation(prop[1],prop[2],prop[0])

for prop in propertiesEffective:
    print "d:%s p:%s r:%s" %(prop[2],prop[1],prop[2])
    #createRelation(prop[1],prop[2],prop[0])

for classe in classes:
    #print "%s subClassOf of %s" %(classe[0],classe[1])
    createClass(classe[0],classe[1])

for classe in classesNames:
    #print "%s " %(classe)
    pass

#f.render('test-output/round-table.gv', view=True)
#f.view()


# for s,p,o in g:
#    print s,p,o
