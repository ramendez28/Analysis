import torch
import torch.nn.functional as F
from torch_geometric.data import Data

# Define the connection via [[Source, Receiver], ...] Syntax
def ConnectivitySourceDestination(Pair_List):
    edge_index = torch.tensor(Pair_List, dtype = torch.long)
    return edge_index.t().contiguous()

def GraphDataObject(Pair_List, Node_Feature = None, Edge_Feature = None, y = None):
    
    connectivity = ConnectivitySourceDestination(Pair_List)
    
    if Node_Feature != None:
        Node_Feature = torch.tensor(Node_Feature, dtype = torch.float)

    if Edge_Feature != None:
        Edge_Feature = torch.tensor(Edge_Feature, dtype = torch.float)
    
    if y != None:
        y = torch.tensor(y, dtype = torch.long)
    
    return Data(x = Node_Feature, edge_index = connectivity, edge_attr = Edge_Feature, y = y)

def GenerateConnectivity(nodes):
    pairs = []
    for i in range(nodes):
        for x in range(nodes):
            # Revert the comment if using classification 
            #if (x != 0 and i > 0) or ( i == 0 and x == 0):
            #     pairs.append([i, x])
            
            # Settings for link prediction
            pairs.append([i, x])

    return pairs

def ProcessDataSample(EventMap):
    TruthLabels = {}
    TruthParticles = {} 
    for i in EventMap:
        TruthLabels[i] = []
        TruthParticles[i] = []

        p = 0
        for x in EventMap[i]["Initial"]:
            TruthLabels[i].append(p)
            TruthParticles[i].append(x)

        p += 1
        for x in EventMap[i]["Products"]:
            TruthLabels[i].append(p)
            TruthParticles[i].append(x)

        for x in EventMap[i]["Products"]:
            p += 1
            for y in x.Decay:
                TruthLabels[i].append(p)
                TruthParticles[i].append(y)

        for x in EventMap[i]["Products"]:
            for y in x.Decay:
                if len(y.Decay) != 0:
                    p += 1
                for t in y.Decay:
                    TruthLabels[i].append(p)
                    TruthParticles[i].append(t)
 
    return TruthLabels, TruthParticles

def DefineNodeFeatures(Particle):
    Node = []
    Node.append(Particle.Energy)
    return Node

def DefineEdgeFeatures(Particle, Connectivity):
    Edge_Feature = []
    for c in Connectivity:
        S = c[0]
        D = c[1]
        p_s = Particle[S]
        p_d = Particle[D]
        
        # Define the feature 
        E_delta = abs(p_d.Energy - p_s.Energy)
        


        Edge_Feature.append([E_delta])
    return None

def Convert_Sample_Object(Map):
    Labels, Particles = ProcessDataSample(Map)
    Data_Objects = []
    for i in Particles:
        P = Particles[i]
        conn = GenerateConnectivity(len(P))
        Edge_Features = DefineEdgeFeatures(P, conn)

        Node_Features = []
        for x in P:
            Node_Features.append(DefineNodeFeatures(x))
        
        Data_Objects.append(GraphDataObject(Pair_List = conn, Node_Feature = Node_Features, Edge_Feature = Edge_Features, y = Labels[i]))
    return Data_Objects

def CalculateLinkProbability(Node_i, Node_j):
    Node_i_T = torch.transpose(Node_i, 0, 0)
    scalar_prod_i_j = torch.dot(Node_i_T, Node_j)
    return float(torch.sigmoid(scalar_prod_i_j))


