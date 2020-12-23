import BaseFunctions.PyGeometric as PG
import BaseFunctions.Plotting as PL
import BaseFunctions.Models as M
import torch

def ClosureData():
    # Define a fake test data set:
    Connections = [[0,1], [1,0], [1,2], [2, 1], [0, 2], [2, 0]]
    Node_Features = [[0, 0], [1, 2], [1, 2]]
    Edge_Features = [[0, 0], [0, 0], [1, 2], [1, 2], [0, 0], [0, 0]]
    y = [3]
    Object = PG.GraphDataObject(Connections, Node_Features, Edge_Features, y)
    Object.train_mask = torch.tensor([1, 1, 1], dtype = torch.bool)
    Object.test_mask = torch.tensor([1, 1, 1], dtype = torch.bool)
    
    return Object

def Test_ConnectivitySourceDestination():
    Connections = [[0,1], [1,0], [1,2], [2, 1]]
    edge_index = PG.ConnectivitySourceDestination(Connections)
    PL.PlotConnectivity(edge_index)

def Test_GraphDataObject():
    
    # Define a fake test data set:
    Connections = [[0,1], [1,0], [1,2], [2, 1], [0, 2], [2, 0]]
    Node_Features = [[1], [1], [0]]
    Edge_Features = [[1,2], [1, 2], [0, 0]]
    Node_Label = [0, 0, 1]
    y = [0, 1]
    Object = PG.GraphDataObject(Connections, Node_Features, Edge_Features, y)

    assert(Object.num_edge_features == len(Edge_Features[0]))
    assert(Object.num_edges == len(Connections))
    assert(Object.num_features == len(Node_Features[0]))
    assert(Object.num_nodes == len(Node_Features))
