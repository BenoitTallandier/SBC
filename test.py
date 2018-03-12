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


createInstance('freiou','Homme')
createInstance('beubeuh','Homme')
createClass('Homme','Homme')
createClass('Homme','Creature')
createRelation('beubeuh','freiou','encule')
createRelation('freiou','T7','encule')
createRelation('T7','beubeuh','encule')



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
classesMere = []

for row in individues:
    if(len(row[0].split("#"))>1 and len(row[1].split("#"))>1):
        instance = row[0].split("#")[1]
        className = row[1].split("#")[1]

        instances.append((instance,className))
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

        newClassesMere = g.query(test)

        for motherClass in newClassesMere:
            if(len(motherClass[0].split("#"))>1):
                motherClassName = motherClass[0].split("#")[1]
                if((className,motherClassName) not in classes):
                    classes.append((className,motherClassName))

        if len(newClassesMere)==0 :
            if className not in classesMere:
                classesMere.append(className)

for classe in instances:
    print "%s instance of %s" %(classe[0],classe[1])
    createInstance(classe[0],classe[1])

for classe in classes:
    print "%s subClassOf of %s" %(classe[0],classe[1])
    createClass(classe[0],classe[1])

for classe in classesMere:
    print "%s " %(classe)



f.view()


# for s,p,o in g:
#    print s,p,o
