import torch
from torch_geometric.data import Data

# Define the connection via [[Source, Receiver], ...] Syntax
def ConnectivitySourceDestination(Pair_List):
    edge_index = torch.tensor(Pair_List, dtype = torch.long)
    return edge_index.t().contiguous()


def GenerateConnectivity(nodes):
    pairs = []
    for i in range(len(nodes)):
        for x in range(len(nodes)):
            pairs.append([i, x])
    return pairs

def DefineEdgeFeatures(Particle, Connectivity, Features):
    Edge_Feature = []
    for c in Connectivity:
        S = c[0]
        D = c[1]
        p_s = Particle[S]
        p_d = Particle[D]
        
        # Define the feature 
        if "dE" in Features:
            E_delta = abs(p_d.Energy - p_s.Energy)
        if "dPx" in Features:
            E_delta = abs(p_d.Px - p_s.Px)
        if "dPy" in Features:
            E_delta = abs(p_d.Py - p_s.Py)
        if "dPz" in Features:
            E_delta = abs(p_d.Pz - p_s.Pz)
        if "dM" in Features:
            E_delta = abs(p_d.Mass - p_s.Mass)
        if "C" in Features:
            E_delta = abs(p_d.Charge - p_s.Charge)
        


        Edge_Feature.append([E_delta])
    return None

def DefineNodeFeatures(Particle, Features):
    Node = []
    Node.append(Particle.Energy)
    return Node

def GraphDataObject(Pair_List, Node_Feature = None, Edge_Feature = None, y = None):
    
    connectivity = ConnectivitySourceDestination(Pair_List)
    
    if Node_Feature != None:
        Node_Feature = torch.tensor(Node_Feature, dtype = torch.float)

    if Edge_Feature != None:
        Edge_Feature = torch.tensor(Edge_Feature, dtype = torch.float)
    
    if y != None:
        y = torch.tensor(y, dtype = torch.long)
    
    return Data(x = Node_Feature, edge_index = connectivity, edge_attr = Edge_Feature, y = y)



