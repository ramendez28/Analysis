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

