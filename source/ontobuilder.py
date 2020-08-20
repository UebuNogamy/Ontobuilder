from owlready2 import *
import types

class Ontobuilder():

    def __init__(self, ontopath):
        self.onto = get_ontology("file://" + ontopath)

    def defineClasses(self, words, policy = "Simple"):

        if len(words) == 0:
            raise ValueError("No classes defined!")

        if policy == "Simple":
            with self.onto as onto:
                for word in words:
                    if onto[word] not in onto.classes():
                        NewClass = type(word, (Thing,), {})
                    else:
                        continue
        elif policy == "Subclass":
            with self.onto as onto:
                for pair in words:
                    if len(pair) != 2: continue
                    if onto[pair[0]] in onto.classes():
                        if onto[pair[1]] in onto.classes():
                            if onto[pair[1]] not in onto[pair[0]].subclasses():
                                NewSubclassAncestors = onto[pair[1]].ancestors()
                                NewSubclassAncestors.add(onto[pair[0]])
                                NewSubclassAncestors.remove(onto[pair[1]])
                                NewSubclass = type(pair[1], tuple(NewSubclassAncestors), {})
                        else:
                            NewSubclass = type(pair[1], (Thing, onto[pair[0]]), {})
                    else:
                        NewAncestor = type(pair[0], (Thing,), {})
                        if onto[pair[1]] in onto.classes():
                            NewSubclassAncestors = onto[pair[1]].ancestors()
                            NewSubclassAncestors.add(onto[pair[0]])
                            NewSubclassAncestors.remove(onto[pair[1]])
                            NewSubclass = type(pair[1], tuple(NewSubclassAncestors), {})
                        else:
                            NewSubclass = type(pair[1], (Thing, onto[pair[0]]), {})
        elif policy == "Equiv":
            with self.onto as onto:
                for pair in words:
                    if len(pair) != 2: continue
                    if onto[pair[0]] in onto.classes():
                        if onto[pair[1]] in onto.classes():
                            if onto[pair[1]] not in onto[pair[0]].subclasses():
                                onto[pair[1]].equivalent_to.append(onto[pair[0]])
                                onto[pair[0]].equivalent_to.append(onto[pair[1]])
                        else:
                            NewSubclass = type(pair[1], (Thing, onto[pair[0]]), {})
                            onto[pair[1]].equivalent_to.append(onto[pair[0]])
                            onto[pair[0]].equivalent_to.append(onto[pair[1]])
                    else:
                        NewAncestor = type(pair[0], (Thing,), {})
                        if onto[pair[1]] in onto.classes():
                            onto[pair[1]].equivalent_to.append(onto[pair[0]])
                            onto[pair[0]].equivalent_to.append(onto[pair[1]])
                        else:
                            NewSubclass = type(pair[1], (Thing, onto[pair[0]]), {})
                            onto[pair[1]].equivalent_to.append(onto[pair[0]])
                            onto[pair[0]].equivalent_to.append(onto[pair[1]])
        else: raise ValueError("Unknown policy!")

    def defineProperty(self, pairs=None, proptype="Subclass_Of", name=None, inverse_property=""):

        if pairs == None: raise ValueError("Input data isn't specified!")
        with self.onto as onto:
            for pair in pairs:
                if proptype == "Subclass_Of":
                    self.defineClasses(pairs, policy="Subclass")
                    break
                elif proptype == "Equal_Class_Of":
                    self.defineClasses(pairs, policy="Equiv")
                    break
                elif proptype == "Object_Property":
                    if name == None: raise ValueError("Property's name is not specified!")
                    if len(pair) != 2: continue
                    else:
                        if onto[name] in onto.object_properties():
                            if inverse_property == "":
                                self.defineClasses(pair)
                                NewPropertyDomain = onto[name].domain
                                NewPropertyDomain.append(onto[pair[0]])
                                NewPropertyRange = onto[name].range
                                NewPropertyRange.append(onto[pair[1]])
                                NewProp = type(name, (ObjectProperty,), dict(domain = NewPropertyDomain, range = NewPropertyRange))
                                continue
                            elif inverse_property in onto.object_properties():
                                self.defineClasses(pair)
                                NewPropertyDomain = onto[name].domain
                                NewPropertyDomain.append(onto[pair[0]])
                                NewPropertyRange = onto[name].range
                                NewPropertyRange.append(onto[pair[1]])
                                NewProp = type(name, (ObjectProperty,), dict(domain = NewPropertyDomain, range = NewPropertyRange, inverse_property = onto[inverse_property]))
                                continue
                            else:
                                self.defineClasses(pair)
                                NewPropertyDomain = onto[name].domain
                                NewPropertyDomain.append(onto[pair[0]])
                                NewPropertyRange = onto[name].range
                                NewPropertyRange.append(onto[pair[1]])
                                NewProp = type(name, (ObjectProperty,), dict(domain=NewPropertyDomain, range=NewPropertyRange))
                                NewPropInversed = type(inverse_property, (ObjectProperty,), dict(domain=NewPropertyRange, range=NewPropertyDomain))
                                NewProp.inverse_property = NewPropInversed
                                NewPropInversed.inverse_property = NewProp
                                continue
                        else:
                            if inverse_property == "":
                                self.defineClasses(pair)
                                NewProp = type(name, (ObjectProperty,), dict(domain = [onto[pair[0]]], range = [onto[pair[1]]]))
                                continue
                            elif inverse_property in onto.object_properties():
                                self.defineClasses(pair)
                                NewProp = type(name, (ObjectProperty,), dict(domain = [onto[pair[0]]], range = [onto[pair[1]]], inverse_property = onto[inverse_property]))
                                continue
                            else:
                                self.defineClasses(pair)
                                NewProp = type(name, (ObjectProperty,), dict(domain=[onto[pair[0]]], range=[onto[pair[1]]]))
                                NewPropInversed = type(inverse_property, (ObjectProperty,), dict(domain=[onto[pair[1]]], range=[onto[pair[0]]]))
                                NewProp.inverse_property = NewPropInversed
                                NewPropInversed.inverse_property = NewProp
                                continue
                elif proptype == "Subproperty":
                    if len(pair) != 2: continue
                    if (onto[pair[0]] not in onto.object_properties()) or (onto[pair[1]] not in onto.object_properties()): continue
                    else:
                        if onto[pair[1]] not in onto[pair[0]].subclasses():
                            if onto[pair[1]] not in onto[pair[0]].subclasses():
                                NewSubpropAncestors = onto[pair[1]].ancestors()
                                NewSubpropAncestors.add(onto[pair[0]])
                                NewSubpropAncestors.remove(onto[pair[1]])
                                if onto[pair[1]].inverse_property == "":
                                    if inverse_property == "":
                                        NewProp = type(pair[1], tuple(NewSubpropAncestors), {})
                                    else:
                                        NewSubpropProperties["inverse_property"] = inverse_property
                                        NewProp = type(pair[1], tuple(NewSubpropAncestors), {})
                                else:
                                    if inverse_property == "":
                                        NewProp = type(pair[1], tuple(NewSubpropAncestors), {})
                                    else:
                                        NewSubpropProperties["inverse_property"] = inverse_property
                                        NewProp = type(pair[1], tuple(NewSubpropAncestors), {})
                elif proptype == "Data_Property":
                    break
                else: raise ValueError("Unknown property type!")

    def deleteEntity(self, entityname):
        with self.onto as onto:
            destroy_entity(onto[entityname])

    def showClasses(self):
        self.onto.load()
        return self.onto.classes()
	
    def showProperties(self, proptype):
        self.onto.load()
        if proptype == "Subclass_Of":
            pairs = []
            for ancestor in self.onto.classes():
                subclasses = list(ancestor.subclasses())
                if len(subclasses) != 0:
                    for subclass in subclasses:
                        pair = [ancestor, subclass]
                        pairs.append(pair)
            return pairs
        elif proptype == "Equal_Class_Of":
            pairs = []
            for ontoclass in self.onto.classes():
                equivclasses = list(ontoclass.equivalent_to)
                if len(equivclasses) != 0:
                    for equivclass in equivclasses:
                        pair = [ontoclass, equivclass]
                        pairs.append(pair)
            return pairs
        elif proptype == "Object_Property":
            properties = []
            for property in self.onto.object_properties():
                prop = {"propname":property, "domain":self.onto[property].domain, "range":self.onto[property].range, "inverse_property":self.onto[property].inverse_property}
                properties.append(prop)
            return properties
        elif proptype == "Subproperty":
            subprops = []
            for property in self.onto.object_properties():
                subproperties = self.onto[property].subclasses()
                if len(subproperties) != 0:
                    for subproperty in subproperties:
                        pair = [property, subproperty]
                        subprops.append(pair)
            return subprops
        elif proptype == "Data_Property":
            pass
        else:
            raise ValueError("Unknown property type!")
	
    def save(self, filetype="rdfxml"):
        self.onto.save(format = filetype)

# if __name__ == "__main__":
#     builder = Ontobuilder("/home/sergey/Рабочий стол/Ontology/Ontology.owl")
#     test = ["A","B","C"]
#     builder.defineClasses(test)
#     pairs = [["A","B"],["B","C"]]
#     builder.defineProperty(pairs=pairs, proptype="Equal_Class_Of")
#     builder.save()
#     print(str(list(builder.showClasses())))
#     print(str(list(builder.showProperties("Subclass_Of"))))
#     onto = get_ontology("file:///home/sergey/test.owl").load()
#     print(str(list(onto.classes())))
#     for cls in onto.classes():
#         print(str(list(cls.equivalent_to)))