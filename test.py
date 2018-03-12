# fsm.py - http://www.graphviz.org/content/fsm

from graphviz import Digraph
import rdflib
f = Digraph('finite_state_machine', filename='fsm.gv')
f.attr(rankdir='LR', size='8,5')

f.attr('node', shape='doublecircle')
f.node('LR_0')
f.node('LR_3')
f.node('LR_4')
f.node('LR_8')

f.attr('node', shape='circle')
f.edge('LR_0', 'LR_2', label='SS(B)')
f.edge('LR_0', 'LR_1', label='SS(S)')
f.edge('LR_1', 'LR_3', label='S($end)')
f.edge('LR_2', 'LR_6', label='SS(b)')
f.edge('LR_2', 'LR_5', label='SS(a)')
f.edge('LR_2', 'LR_4', label='S(A)')
f.edge('LR_5', 'LR_7', label='S(b)')
f.edge('LR_5', 'LR_5', label='S(a)')
f.edge('LR_6', 'LR_6', label='S(b)')
f.edge('LR_6', 'LR_5', label='S(a)')
f.edge('LR_7', 'LR_8', label='S(b)')
f.edge('LR_7', 'LR_5', label='S(a)')
f.edge('LR_8', 'LR_6', label='S(b)')
f.edge('LR_8', 'LR_5', label='S(a)')

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

for classe in classes:
    print "%s subClassOf of %s" %(classe[0],classe[1])

for classe in classesMere:
    print "%s " %(classe)


# for s,p,o in g:
#    print s,p,o
