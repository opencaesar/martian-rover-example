#Author: Sophia Salas Cordero
#Functions to calculate network metrics and store results as dataframes and a transversing function for potential obsolescence propagation

import networkx as nx
import pandas as pd

from networkx.algorithms import community
from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges

from lib.project_functions import fromDataToTable

#Degree

def calculateDegree(G,df,name):
    degrees = dict(nx.degree(G))
    nx.set_node_attributes(G, name='degree', values=degrees)

    degree_df = pd.DataFrame(G.nodes(data='degree'), columns=['node', 'degree'])

    degree_df=normalizeDegree(degree_df,name)

    df = pd.merge(df, degree_df)
    # inner_merged_total = inner_merged_total.drop(["node"],axis=1)
    # inner_merged_total.sort_values(by=["degree","node"], ascending=[False,True])

    return df,degree_df


def normalizeDegree(degree_df,name):
    max_degree= degree_df['degree'].max()
    degree_df[name]=(degree_df['degree']/max_degree)

    return degree_df


#Betweenness Centrality

def calculateBetweennessC(G,df):
    betweenness_centrality = nx.betweenness_centrality(G)
    nx.set_node_attributes(G, name='betweenness', values=betweenness_centrality)

    betweenness_df = pd.DataFrame(G.nodes(data='betweenness'), columns=['node', 'betweenness'])
    # betweenness_df = betweenness_df.sort_values(by='betweenness', ascending=False)

    df = pd.merge(df, betweenness_df)

    return df,betweenness_df

#Eigenvector centrality

def calculateEigenvectorC(G,df):
    if nx.is_directed(G):
        Reversed_G=G.reverse() # the graph is reversed in order to take into account that output is more important than input (as far as potential impact is being considered) as by default the nx algorithm takes it into account the opposite way for eigenvector centrality
    else: Reversed_G=G

    eigenvector=nx.eigenvector_centrality(Reversed_G)
    nx.set_node_attributes(G, name='eigenvector', values=eigenvector)

    eigenvector_df = pd.DataFrame(G.nodes(data='eigenvector'), columns=['node', 'eigenvector'])
    # eigenvector_df = eigenvector_df.sort_values(by='eigenvector', ascending=False)
    df = pd.merge(df, eigenvector_df)

    return df,eigenvector_df


#Closeness Centrality closeness_centrality

def calculateClosenessC(G,df):
    if nx.is_directed(G):
        Reversed_G=G.reverse() # the graph is reversed in order to take into account that output is more important than input (as far as potential impact is being considered) as by default the nx algorithm takes it into account the opposite way for closeness centrality 
    else: Reversed_G=G
    
    closeness_centrality= nx.closeness_centrality(Reversed_G)
    nx.set_node_attributes(G, name='closeness',values=closeness_centrality)

    closeness_df= pd.DataFrame(G.nodes(data='closeness'),columns=['node','closeness'])

    df= pd.merge(df,closeness_df)

    return df,closeness_df

def calculateOutDegreeCentrality(G,df):
    outdegree_centrality = nx.out_degree_centrality(G)
    nx.set_node_attributes(G, name='outdegree_centrality', values=outdegree_centrality)

    outdegree_centrality_df = pd.DataFrame(G.nodes(data='outdegree_centrality'), columns=['node', 'outdegree_centrality'])
    # betweenness_df = betweenness_df.sort_values(by='betweenness', ascending=False)

    df = pd.merge(df, outdegree_centrality_df)

    return df,outdegree_centrality_df


def calculateOutDegree(Di_graph,df):
    Out_degree = dict(Di_graph.out_degree())
    nx.set_node_attributes(Di_graph, name='Out_degree', values=Out_degree)
    out_degree_df = pd.DataFrame(Di_graph.nodes(data='Out_degree'), columns=['node', 'Out_degree'])


    df = pd.merge(df, out_degree_df)


    return df,out_degree_df

def calculateInDegree(Di_graph,df):
    In_degree = dict(Di_graph.in_degree())
    nx.set_node_attributes(Di_graph, name='In_degree', values=In_degree)
    in_degree_df = pd.DataFrame(Di_graph.nodes(data='In_degree'), columns=['node', 'In_degree'])


    df = pd.merge(df, in_degree_df)


    return df,in_degree_df

def calculateAllMetrics(Di_graph,df):
    metric_table_Di=fromDataToTable(df)
    metric_table_Di,out_degreeC=calculateOutDegreeCentrality(Di_graph,metric_table_Di)
    metric_table_Di,BC_Di=calculateBetweennessC(Di_graph,metric_table_Di)
    metric_table_Di,CC_Di=calculateClosenessC(Di_graph,metric_table_Di)
    metric_table_Di,EC_Di=calculateEigenvectorC(Di_graph,metric_table_Di)

    return metric_table_Di

#Communities

def calculateCommunities(G,df):

    communities = community.greedy_modularity_communities(G)

    # Create empty dictionary
    modularity_class = {}

    #Loop through each community in the network
    for community_number, community_n in enumerate(communities):
        #For each member of the community, add their community number
        for name in community_n:
            modularity_class[name] = community_number


    nx.set_node_attributes(G, modularity_class, 'modularity_class')

    communities_df = pd.DataFrame(G.nodes(data='modularity_class'), columns=['node', 'modularity_class'])

    communities_df = communities_df.sort_values(by='modularity_class', ascending=False)
    return df,communities_df

# Metric Charts

def metric_Chart(metric_df,metric,num_nodes_to_inspect):

    metric_df.sort_values(by=metric, ascending=False)[:num_nodes_to_inspect].plot(x='elements', y=metric, kind='barh').invert_yaxis()

    return metric_df

def all_metric_Chart(metric_df,i,num_nodes_to_inspect):
    # metric_df.sort_values(by='degree', ascending=False)

    for column in metric_df.columns[i:]:
        metric_df.sort_values(by=column, ascending=False)[:num_nodes_to_inspect].plot(x='elements', y=column, kind='barh').invert_yaxis()
    




#-----------------------------------------------------------------------------------------------------------------------------------
# Taking into account that the propagation of a posible change to a function should go from "child" function to "parent function"

def Potential_Obso_Prop(dataframe1,nodes,n,i=None,df_to_viz=None,df_prop=pd.DataFrame()):
    
    if df_to_viz is None:
        df_to_viz=pd.DataFrame()
        
    dataframe=dataframe1.copy(deep=True) #deep copy of dataframe to not alter input dataframe
    if not i : 
        i=1

    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4]) # a list of ordinal numbers up to n-th

    if n>0:
        results=[] # propagation at each "n" level
        elements=[] # list of n+1 neighbors of the node
        for node in nodes:
            node_type=dataframe.loc[dataframe['element1'] == node,'element1type'] #to extract the value of the type of the node from dataframe
            if not node_type.empty : 
                node_type=node_type.values[0]
            else : 
                node_type=dataframe.loc[dataframe['element2'] == node,'element2type']
                if not node_type.empty :
                    node_type=node_type.values[0]
                else:
                    # print("blabla",node)
                    continue
            
            # print(node)
            # print(node_type)
            if node_type == "Requirement":

                propC_F=dataframe[(dataframe['relation']=='specifies')&(dataframe["element1"]==node)][['element2']] # To find (component or function) being specified by the requirement
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='specifies')&(dataframe["element1"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='specifies')&(dataframe["element1"]==node)].index,inplace=True)

                propReq_down=dataframe[(dataframe['relation']=='refines')&(dataframe["element1"]==node)][['element2']] # To find requirement that refines the origin node requirement
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='refines')&(dataframe["element1"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='refines')&(dataframe["element1"]==node)].index,inplace=True)

                propReq_up=dataframe[(dataframe['relation']=='refines')&(dataframe["element2"]==node)][['element1']] # To find requirement that is refined by origin node requirement
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='refines')&(dataframe["element2"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='refines')&(dataframe["element2"]==node)].index,inplace=True)
                
                total_prop=[propC_F,propReq_down,propReq_up]#list gathering the propagations of "node"

                for df in total_prop: # rename the column name to the nth
                    df.columns=[ordinal(i)]

                df_prop=pd.concat(total_prop,axis=0)  #unite the results in one column
                elements.extend(df_prop[ordinal(i)].tolist())
                df_prop.reset_index(drop=True,inplace=True)  # remove the index from the previous dataframe they appeared at 
                lst=[] 
                for a in df_prop.index:  #create a list of nodes for the n-1 step in order for the rows to show a propagation line
                    lst.append(node)
                if lst:
                    origin=pd.DataFrame(lst) #create dataframe of the components in the list
                    origin.columns=[ordinal(i-1)] # to name columns of the origin, so i-1
                    df_prop=pd.concat([origin, df_prop],axis=1) # origin + 1 level propagation
                    results.append(df_prop) #to gather the neighbors per previous level node


                
            if node_type == "Component":

                propComp=dataframe[(dataframe['relation']=='aggregates')&(dataframe["element2"]==node)][['element1']] #higher hierarchical level of the component "higher assembly"
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='aggregates')&(dataframe["element2"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='aggregates')&(dataframe["element2"]==node)].index,inplace=True)

                propFun=dataframe[(dataframe['relation']=='performs')&(dataframe["element1"]==node)][["element2"]] #Function that is performed by the component
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='performs')&(dataframe["element1"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='performs')&(dataframe["element1"]==node)].index,inplace=True)

                propReq=dataframe[(dataframe['relation']=='specifies')&(dataframe["element2"]==node)][['element1']] #Requirement that specifies the component
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='specifies')&(dataframe["element2"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='specifies')&(dataframe["element2"]==node)].index,inplace=True)

                total_prop=[propComp,propFun,propReq] #list gathering the propagations of "node"
                for df in total_prop: # rename the column name to the nth
                    df.columns=[ordinal(i)]

                df_prop=pd.concat(total_prop,axis=0)  #unite the results in one column
                elements.extend(df_prop[ordinal(i)].tolist())
                df_prop.reset_index(drop=True,inplace=True)  # remove the index from the previous dataframe they appeared at 
                lst=[]
                for a in df_prop.index:  #create a list of nodes for the n-1 step in order for the rows to show a propagation line
                    lst.append(node)
                if lst:
                    origin=pd.DataFrame(lst) #create dataframe of the components in the list
                    origin.columns=[ordinal(i-1)] # to name columns of the origin, so i-1
                    df_prop=pd.concat([origin, df_prop],axis=1) # origin + 1 level propagation
                    results.append(df_prop) #to gather the neighbors per previous level node
                
            
            if node_type == "Function":

                PropComp=dataframe[(dataframe['relation']=='performs')&(dataframe["element2"]==node)][["element1"]] # to find the component that performs the function
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='performs')&(dataframe["element2"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='performs')&(dataframe["element2"]==node)].index,inplace=True)

                propReq=dataframe[(dataframe['relation']=='specifies')&(dataframe["element2"]==node)][['element1']] # Requirement that specifies the function
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='specifies')&(dataframe["element2"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='specifies')&(dataframe["element2"]==node)].index,inplace=True)

                # between functions there can be 2 types of relation: invokesComp & invokesAlt
                #for invokesComp:

                PropFun_simple_up=dataframe[(dataframe['relation']=='invokesComp')&(dataframe["element2"]==node)][["element1"]]
                df_to_viz=pd.concat([df_to_viz,dataframe[(dataframe['relation']=='invokesComp')&(dataframe["element2"]==node)]])
                dataframe.drop(dataframe[(dataframe['relation']=='invokesComp')&(dataframe["element2"]==node)].index,inplace=True)


                total_prop=[PropComp,propReq,PropFun_simple_up] #list gathering the propagations of "node"

                for df in total_prop: # rename the column name to the nth
                    df.columns=[ordinal(i)]

                df_prop=pd.concat(total_prop,axis=0)  #unite the results in one column
                elements.extend(df_prop[ordinal(i)].tolist())
                df_prop.reset_index(drop=True,inplace=True)  # remove the index from the previous dataframe they appeared at 
                lst=[]
                for a in df_prop.index:  #create a list of nodes for the n-1 step in order for the rows to show a propagation line
                    lst.append(node)
                if lst:
                    origin=pd.DataFrame(lst) #create dataframe of the components in the list
                    origin.columns=[ordinal(i-1)] # to name columns of the origin, so i-1
                    df_prop=pd.concat([origin, df_prop],axis=1) # origin + 1 level propagation
                    results.append(df_prop) #to gather the neighbors per previous level node
                

        if results:
        
            df_prop=pd.concat(results,axis=0) # dataframe of the propagation at each "n" level
        else :
            # print("It does enter here")
            # print(nodes)
            return pd.DataFrame(columns=[ordinal(i),ordinal(i-1)])
            
        # print(df_prop.head()) # to check propagation per step
        if n ==1: 
            # print(df_to_viz)
            return df_prop

        else :
            return df_prop.merge(Potential_Obso_Prop(dataframe,elements,n-1,i+1,df_to_viz),how="outer").fillna("-") #to call recursively the Prop function until the nth step
    

    if n<=0:
        print("There can't be negative propagation")