import networkx as nx
import matplotlib.pyplot as plt
import torch

def PlotConnectivity(edge_index, weights = [], direct = "Example.pdf"):
    G = nx.Graph()
    
    for i in range(int(edge_index[0].max())+1):
        G.add_node(i)
        
    w = 0
    for i in torch.stack((edge_index[0], edge_index[1]), dim = 1):
        # Determine the weight by context of the size of the vector
        if len(weights) == 0:
            weight = 0
        else:
            weight = round(float(weights[w]), 5)
            w += 1
        
        G.add_edge(int(i[0]), int(i[1]), weight = weight)
    pos = nx.random_layout(G)
    nx.draw(G, pos)
    
    if len(weights) != 0:
        labels = nx.get_edge_attributes(G, "weights")
        nx.draw_networkx_edge_labels(G, pos, edge_labels = labels)
    plt.savefig(direct)
