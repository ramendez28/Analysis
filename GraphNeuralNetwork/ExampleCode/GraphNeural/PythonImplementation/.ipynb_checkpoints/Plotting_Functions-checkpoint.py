import networkx as nx
import matplotlib.pyplot as plt
import torch

def CreateGraphOutput(edge_index, weights):
    G = nx.Graph()
    w = 0  

    for i in range(int(edge_index[0].max())+1):
        G.add_node(i)

    for i in torch.stack((edge_index[0], edge_index[1]), dim =1):
        G.add_edge(int(i[0]), int(i[1]), weight = round(float(weights[w]), 5))
        w = w+1

    pos = nx.random_layout(G)
    nx.draw(G, pos)
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels = labels)
    plt.savefig("example.png")

        
    