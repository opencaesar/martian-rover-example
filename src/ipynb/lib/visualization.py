#Author: Sophia Salas Cordero
#This library contains modified content of https://github.com/melaniewalsh/Intro-Cultural-Analytics/ that was licensed under GNU General Public License v3.0

import networkx as nx
from bokeh.io import output_notebook, show, save, output_file
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine
from bokeh.plotting import figure, from_networkx

# Color Palletes
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8, d3
from bokeh.transform import linear_cmap

# Community module 

from networkx.algorithms import community

def simpleVisualization(G,title):
    #title = 'Dependency Graph' select name when calling function

    #Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [("Element", "@index")]

    #Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips = HOVER_TOOLTIPS,
                tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                sizing_mode="scale_width", title=title) #set sizing mode to adjust to window display width
                

    network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

    #Set node size and color
    network_graph.node_renderer.glyph = Circle(size=15, fill_color='skyblue')

    #Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

    #Add network graph to the plot
    plot.renderers.append(network_graph)

    show(plot)
    save(plot, filename=title+".html")
    output_file(title+".html")


# To modify the node size for vizualization based on the degree of the node

def modifyNodeViz(G):
    number_to_adjust_by = 10  #to adjust for the smaller nodes to still be visible
    degrees = dict(nx.degree(G))
    nx.set_node_attributes(G, name='degree', values=degrees)
    adjusted_node_size={k:v+number_to_adjust_by for k,v in degrees.items()}
    nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)
    # adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(G)])
    # nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

    # in case only the out degree would be needed for sizing
    # adjusted_node_size = dict([(node, Out_degree+number_to_adjust_by) for node, Out_degree in G.out_degree()])
    # nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)
    


#-------------------------------
# Visualization with Node Size and colored by Attribute (Degree)

#Degree: Number of connections that a node has with other nodes in the network

def sizeAndColoringByDegree(G):

    modifyNodeViz(G)

    #Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed

    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'adjusted_node_size'


    #Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
    color_palette = Blues8

    # If you want a predetermined title and not one input by the user
    title = 'Visualization_with_node_size_according_to_degree' 

    #Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [
        ("Element", "@index"),
            ("Degree", "@degree")
    ]

    #Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips = HOVER_TOOLTIPS,
                tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1), title=title)

    #Create a network graph object
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html\
    network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

    #Set node sizes and colors according to node degree (color as spectrum of color palette)
    minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
    maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
    # LinearColorMapper: Map numbers in a range [low, high] linearly into a sequence of colors (a palette).
    network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

    #Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

    plot.renderers.append(network_graph)

    output_notebook()
    show(plot)
    # output_file(title+".html")
    # show(plot)
    save(plot, filename=(title+".html")) 
    
    

#-------------------------------
# Visualization with communities

def communitiesVisualization(G,types):
    modifyNodeViz(G)
    
    from networkx.algorithms import community  

    communities = community.greedy_modularity_communities(G)

    # Community: a subset of nodes that are densely connected to each other and loosely connected to the nodes in the other communities in the same graph
    # Add modularity class and color as attributes to network graph

    # Create empty dictionaries
    modularity_class = {}
    modularity_color = {}

    my_palette=d3['Category20'][20] # To add 20 colors , 1 color is needed per community 

    #Loop through each community in the network
    for community_number, community in enumerate(communities):
        #For each member of the community, add their community number and a distinct color
        for name in community: 
            try:
                modularity_class[name] = community_number
                modularity_color[name] = my_palette[community_number]
            except:
                print(community_number)
    
    # Add modularity class and color as attributes from the network above
    nx.set_node_attributes(G, modularity_class, 'modularity_class')
    nx.set_node_attributes(G, modularity_color, 'modularity_color')
    nx.set_node_attributes(G, types, 'type')

    from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges

    #Choose colors for node and edge highlighting
    # node_highlight_color = 'white'
    # edge_highlight_color = 'black'
    node_highlight_color = 'red'
    edge_highlight_color = 'red'

    #Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'modularity_color'

    #Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
    color_palette = Blues8

    # In case a predetermined title is preferred
    title = 'Interactive_visualization'

    #Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [
        ("Element", "@index"),
            ("Degree", "@degree"),
            ("Type", "@type"),
            ("betweenness", "@betweenness"),
            ("Modularity Class", "@modularity_class"),
            ("Modularity Color", "$color[swatch]:modularity_color"),
    ]



    #Create plot, hover option active, select tools and set title for vizualization
    plot = figure(tooltips = HOVER_TOOLTIPS,
                tools="pan,wheel_zoom,save,reset,tap", active_scroll='wheel_zoom',
                sizing_mode="fixed", title=title)



    #Create network graph object with networkx
    
    network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

    #Set node sizes and colors according to node degree (color as category from attribute)
    network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
    #Set node highlight colors
    network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
    network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

    #Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
    #Set edge highlight colors
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

    #Highlight nodes and edges by hovering and/or clicking on the node
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = NodesAndLinkedEdges()

    plot.renderers.append(network_graph)


    output_notebook()
    show(plot)
    # output_file(title+".html")
    # show(plot)
    save(plot, filename=(title+".html"))
    # save(plot, filename=(title+".html"))
    # show(plot)
    # output_file(title+".html")
    
    