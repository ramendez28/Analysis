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
            #if i == x:
            #    continue 
            pairs.append([i, x])
    return pairs

def DefineEdgeFeatures(Particle, Connectivity, Features):
    Edge_Feature = []
    for c in Connectivity:
        Edge = []
        S = c[0]
        D = c[1]
        p_s = Particle[S]
        p_d = Particle[D]
        
        # Define the feature 
        if "dE" in Features:
            dE = abs(p_d.Energy - p_s.Energy)
            Edge.append(dE)
        if "dPx" in Features:
            dPx = abs(p_d.Px - p_s.Px)
            Edge.append(dPx)
        if "dPy" in Features:
            dPy = abs(p_d.Py - p_s.Py)
            Edge.append(dPy)
        if "dPz" in Features:
            dPz = abs(p_d.Pz - p_s.Pz)
            Edge.append(dPz)
        if "dM" in Features:
            dM = abs(p_d.Mass - p_s.Mass)
            Edge.append(dM)
        Edge_Feature.append(Edge) 
    return Edge_Feature

def DefineNodeFeatures(Particle, Features):
    Nodes = []
    for p in Particle:
        Node = []
    
        # Define the feature 
        if "E" in Features:
            Node.append(p.Energy)
        if "Px" in Features:
            Node.append(p.Px)
        if "Py" in Features:
            Node.append(p.Py)
        if "Pz" in Features:
            Node.append(p.Pz)
        if "M" in Features:
            Node.append(p.Mass)
        if "C" in Features:
            Node.append(p.Charge)
        Nodes.append(Node)
    return Nodes

def GraphDataObject(Pair_List, Node_Feature = None, Edge_Feature = None, y = None, mask = None):
    
    connectivity = ConnectivitySourceDestination(Pair_List)
    
    if Node_Feature != None:
        Node_Feature = torch.tensor(Node_Feature, dtype = torch.float)

    if Edge_Feature != None:
        Edge_Feature = torch.tensor(Edge_Feature, dtype = torch.float)
    
    if y != None:
        y = torch.tensor(y, dtype = torch.long)

    if mask != None:
        mask = torch.tensor(mask, dtype = torch.bool)
    
    D = Data(x = Node_Feature, edge_index = connectivity, edge_attr = Edge_Feature, y = y)
    D.mask = mask
    return D


