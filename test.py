# fsm.py - http://www.graphviz.org/content/fsm

from graphviz import Digraph
import rdflib

limitInstance = raw_input("Nb max instance(0=inf) : ")
maxProperties = raw_input("Nb max properties(0=inf) : ")
afficherABox = raw_input("Afficher ABox (O/N) : ")

if(afficherABox=="O" or afficherABox=="o"):
    afficherABox = True
else:
    afficherABox = False

f = Digraph('hierarchie', filename='visualisation.gv')
f.attr(rankdir='LR', size='8,5')


def createClass (nameClass,parentName):
    f.attr('node', shape='oval')
    f.edge(nameClass,parentName,'rdf:subClassOf')


def createInstance (nameInstance,className):
    f.attr('node', shape='oval')
    f.node(className)
    f.attr('node', shape='box')
    f.edge(nameInstance,className,'rdf:type')

def createRelation (relationRange,domain,relationName):
    f.attr('node', shape='oval')
    f.node(relationRange)
    f.node(domain)
    f.edge(relationRange,domain,relationName)



g=rdflib.Graph()
g.load('ontology-rdf.owl')

instances = []
classes = []
classesNames = []
properties = []
propertiesEffective = []
me = False

classMoreInstancied = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?type (COUNT(?sub) as ?subCount)
    WHERE {
        ?sub rdf:type ?type.
        ?sub a ?class.
        FILTER( ?class = owl:NamedIndividual).
        FILTER (?type != owl:NamedIndividual)
    }
    GROUP BY ?type
    ORDER BY DESC(?subCount)
    """+("LIMIT "+str(limitInstance) if(int(limitInstance))>0 else "")
#print (classMoreInstancied)
classMoreInstancied = g.query(classMoreInstancied)

for cla in classMoreInstancied:
    if me==False:
        me = cla[0].split("#")[0]
    individues = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX me: <"""+me+"""#>
            SELECT ?sub ?type
            WHERE {
                ?sub rdf:type ?type.
                ?sub a me:"""+cla[0].split("#")[1]+""".
                FILTER (?type != owl:NamedIndividual)
                }"""
    #print (individues)
    individues = g.query(individues)


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
    SELECT DISTINCT ?p ?r ?d (COUNT(?p) as ?propertiesCount)
    WHERE {
    {?p rdfs:range me:"""+className+"""} UNION {?p rdfs:domain me:"""+className+"""}.
    ?p rdfs:range ?r.
    ?p rdfs:domain ?d.
    }
    GROUP BY ?p
    ORDER BY DESC(?propertiesCount)
    """+("LIMIT "+str(maxProperties) if (int(maxProperties)>0) else "" )

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
    propertiesQuery2= """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX me: <"""+me+"""#>    SELECT  ?d ?r
    WHERE
    {
	?d me:"""+prop[0]+""" ?r.
    }
    """

    rows = g.query(propertiesQuery2)

    for row in rows:
        if(len(row[0].split("#"))>1):
            domainInstance = row[0].split("#")[1]
        if(len(row[0].split("#"))>1):
            rangeInstance = row[1].split("#")[1]
        newRow = (domainInstance,prop[0],rangeInstance)

        if newRow not in propertiesEffective:
            propertiesEffective.append(newRow)

    propertiesQuery2 = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX me: <"""+me+"""#>
        SELECT  DISTINCT ?classDomain ?classRange
        WHERE
        {
        	?d me:"""+prop[0]+""" ?r.
        	?d rdf:type ?classDomain.
        	?r rdf:type ?classRange.
        	FILTER (?classDomain != owl:NamedIndividual)
        	FILTER (?classRange != owl:NamedIndividual)
        }
    """

    rows = g.query(propertiesQuery2)

    i=0
    allRangeEqual = True
    allDomainEqual = True
    oldRange = prop[1]
    oldDomain = prop[2]
    propertyName = prop[0]
    for row in rows:
        if(i==0):
            newRange = row[1]
            newDomain = row[0]
            i+=1
        if (allRangeEqual and newRange != row[1]):
            allRangeEqual = False
        if (allDomainEqual and newDomain != row[0]):
            allDomainEqual = False
        if (not allRangeEqual and not allDomainEqual):
            break

    if(len(newRange.split("#"))>1):
        newRange = newRange.split("#")[1]
    if(len(newDomain.split("#"))>1):
        newDomain = newDomain.split("#")[1]

    if (allRangeEqual and not allDomainEqual):
        properties.remove(prop)
        newRow = (propertyName,oldDomain,newRange)
    elif (not allRangeEqual and allDomainEqual):
        properties.remove(prop)
        newRow = (propertyName,newDomain,oldRange)
    elif (allRangeEqual and allDomainEqual):
        properties.remove(prop)
        newRow = (propertyName,newDomain ,newRange)
    else :
        newRow = prop

    if newRow not in properties:
        properties.append(newRow)


if(afficherABox):
    for classe in instances:
        for c in classes:
            if(c[0]==classe[1] or classe[1] == c[1]):
                createInstance(classe[0],classe[1])
                break
        #print "%s instance of %s" %(classe[0],classe[1])

for prop in properties:
    print "prop:%s range:%s dom:%s" %(prop[0],prop[1],prop[2])
    prop1OK = False;
    prop2OK = False;
    for c in classes:
        if (prop[1] == c[0] or prop[1] == c[1]):
            prop1OK = True
        if (prop[2] == c[0] or prop[2] == c[1]):
            prop2OK = True
        if(prop1OK and prop2OK):
            createRelation(prop[1],prop[2],prop[0])
            break

if(afficherABox):
    for prop in propertiesEffective:
        #print "d:%s p:%s r:%s" %(prop[0],prop[1],prop[2])
        prop0OK = False
        prop2OKK =False
        for i in instances :
            if (prop[0] == i[0]):
                prop0OK = True
            if (prop[2] == i[0]):
                prop2OKK = True
            if (prop0OK and prop2OKK):
                createRelation(prop[0],prop[2],prop[1])
                break
        #if (prop[0] in instances and prop[2] in instances):

for classe in classes:
    print "%s subClassOf of %s" %(classe[0],classe[1])
    createClass(classe[0],classe[1])

for classe in classesNames:
    #print "%s " %(classe)
    pass

#f.render('test-output/round-table.gv', view=True)
f.view()


# for s,p,o in g:
#    print s,p,o
