#Author: Sophia Salas Cordero
#Functions to create dataframes and graphs

import xml.etree.ElementTree as ET
import pandas as pd
import networkx as nx

# XML general file to dictionary parsing

# Parsing for query results in xml which follow the pattern: element1, relation, element2, element1type, element2type
#Parsing from xml to pandas
def create_DF(filename):

    #pasing file into tree 

    tree=ET.parse(filename)

    ns="{http://www.w3.org/2005/sparql-results#}"

    root=tree.getroot()

    lst = []
    types={}

    for results in root.findall(ns+'results'):
        for result in results:
            bindings = result.findall(ns+"binding")
            for binding in bindings:
                if binding.attrib['name']=="element1":
                    element1=binding.find(ns+"uri").text[binding.find(ns+"uri").text.find("#")+1:]
                if binding.attrib['name']=="relation":
                    relation=binding.find(ns+"uri").text[binding.find(ns+"uri").text.find("#")+1:]
                if binding.attrib['name']=="element2":
                    element2=binding.find(ns+"uri").text[binding.find(ns+"uri").text.find("#")+1:]
                if binding.attrib['name']=="element1type":
                    element1type = binding.find(ns+"literal").text
                    types[element1]=element1type
                if binding.attrib['name']=="element2type":
                    element2type = binding.find(ns+"literal").text
                    types[element2]=element2type
                
            lst.append([element1,element2,element1type,element2type,relation])
    return pd.DataFrame(lst, columns=['element1','element2','element1type','element2type','relation']), types  #pandas DataFrame

# Parsing query results in xml follow the pattern: (Functional requirements - Function - Performing element)
# Parsing XML file for functional requirements parsing to pandas

def createFunctionalReq_DF(filename):

    #pasing file into tree 

    tree=ET.parse(filename)

    ns="{http://www.w3.org/2005/sparql-results#}"

    root=tree.getroot()

    lst=[]

    for results in root.findall(ns+'results'):
        for result in results:
            bindings = result.findall(ns+"binding")
            for binding in bindings:
                if binding.attrib['name']=="functionalRqmt":
                    functionalRqmt=binding.find(ns+"uri").text[binding.find(ns+"uri").text.find("#")+1:]
                    functionalRqmt_type = "Requirement"
                if binding.attrib['name']=="performingElement":
                    performingElement=binding.find(ns+"uri").text[binding.find(ns+"uri").text.find("#")+1:]
                    #performingElement_type = "Performing Element"
                    performingElement_type = "Component"
                if binding.attrib['name']=="function":
                    function=binding.find(ns+"uri").text[binding.find(ns+"uri").text.find("#")+1:]
                    function_type = "Function"
                

            # Allocating relations for Functional pattern    
           
            lst.append([functionalRqmt,performingElement,functionalRqmt_type,performingElement_type,"specifies"])
            lst.append([functionalRqmt,function,functionalRqmt_type,function_type,"specifies"])
            lst.append([performingElement,function,performingElement_type,function_type,"performs"])

    return pd.DataFrame(lst, columns=['element1','element2','element1type','element2type','relation']) 

# Build Graph in networkx

def createGraph(filename,filename2=None):
    #if the graph needs data from more than one query result file, the base is model_data, extended with model_data2

    model_data, types = create_DF(filename)
    if filename2:
        model_data2=createFunctionalReq_DF(filename2)
        model_data=pd.concat([model_data,model_data2], axis=0)
    
    model_data.drop_duplicates(inplace=True)
    model_data.reset_index(inplace=True,drop=True)
     #Building Graph
    G = nx.from_pandas_edgelist(model_data, 'element1', 'element2', 'relation')

    return G, model_data,types

#Function to create a directed graph
def createDiGraph(filename,filename2=None):
    #if the graph needs data from more than one query result file, the base is model_data, extended with model_data2

    model_data, types = create_DF(filename)
    if filename2:
        model_data2=createFunctionalReq_DF(filename2)
        model_data=pd.concat([model_data,model_data2], axis=0)
    
    model_data.drop_duplicates(inplace=True)
    model_data.reset_index(inplace=True,drop=True)

    # To create the "backwards relations" for everything but aggregates, invokesAlt, and invokesComp
    a=model_data[(model_data["relation"]!="invokesAlt")&(model_data['relation']!="aggregates")&(model_data['relation']!="invokesComp")] 
    a=a.rename(columns={"element1":"element2","element2":"element1","element1type":"element2type","element2type":"element1type"})
    model_data=pd.concat([model_data,a])
    model_data.reset_index(inplace=True,drop=True) # to reniciate the indexes of the rows in a, that by default would have had the index of the model_data row they are copying

    #Change "flow" direction in the case of the aggregates relation and invokesComp
    b=model_data[(model_data['relation']=="aggregates")|(model_data['relation']=="invokesComp")] # To create the flow of "change" be from lower level element to higher level
    model_data.drop(model_data[model_data['relation']=="aggregates"].index,inplace=True) # To delete the previous row where the flow of "change" was from a higher level component to a lower level component
    model_data.drop(model_data[model_data['relation']=="invokesComp"].index,inplace=True) # To delete the previous row where the flow of "change" was from a higher level function to a lower level function
    b=b.rename(columns={"element1":"element2","element2":"element1","element1type":"element2type","element2type":"element1type"})
    model_data=pd.concat([model_data,b])
    model_data.reset_index(inplace=True,drop=True) # to reniciate the indexes of the rows in b, that by default would have had the index of the model_data row they are copying

    #get rid of invokesAlt relations
    model_data.drop(model_data[model_data['relation']=="invokesAlt"].index,inplace=True) # To delete the rows where the flow of "change" would involve an invokesAlt
    model_data.reset_index(inplace=True,drop=True) # to reniciate the indexes of the rows in a, that by default would have had the index of the model_data row they are copying

    
     #Building Graph
    G = nx.from_pandas_edgelist(model_data,source= 'element1', target='element2', edge_attr='relation',create_using=nx.DiGraph())

    return G, model_data,types

    # To create graph only of Fun-Req-Comp, otherwise, Use createGraph
def createGraph2(filename,filename2=None,funReq=False):
    #if the graph needs data from more than one query result file, the base is filename, extended with filename2
    if funReq:
        model_data=createFunctionalReq_DF(filename)
    else:
        model_data = create_DF(filename)
        if filename2:
            model_data2=createFunctionalReq_DF(filename2)
            model_data=pd.concat([model_data,model_data2], axis=0)
    
    model_data.drop_duplicates(inplace=True)

     #Building Graph
    G = nx.from_pandas_edgelist(model_data, 'element1', 'element2', 'relation')

    return G, model_data

def fromDataToTable(model_data):
    el1=model_data[["element1","element1type"]]
    el1.columns=["node",'element_type']
    el2=model_data[["element2","element2type"]]
    el2.columns=["node",'element_type']
    table=pd.concat([el1,el2],ignore_index=True)
    #full_table.duplicated(subset=['element','element_type']) # to check if there are duplicates
    table=table.drop_duplicates(subset=['node','element_type'],ignore_index=True) # to get rid of duplicate rows
    table["elements"]=table["node"]+" ("+table["element_type"]+") "

    return table

def searchType(metric_table_Di):
    element= input("Type element name to confirm its type")
    return metric_table_Di[metric_table_Di["node"]==element]["element_type"].squeeze()
