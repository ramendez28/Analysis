import BaseFunctions.PyGeometric as PG
import BaseFunctions.Plotting as PL
import BaseFunctions.Models as M
import torch
from torch_geometric.datasets import Planetoid 
import torch.nn.functional as F

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

def Test_GCN_Net():
    dataset = Planetoid(root = "/tmp/Cora", name = "Cora")
    data = dataset[0]
    model = M.GCN_Net(data, 16)
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01, weight_decay = 5e-4)
    model.train()

    print(data.edge_index)
    print(data.x.shape) 
    print(data.num_node_features)
    print(data.y[data.train_mask])
    for epoch in range(200):
        optimizer.zero_grad()
        out = model(data)
        loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        optimizer.step()

    model.eval()
    _, pred = model(data).max(dim = 1)
    correct = int(pred[data.test_mask].eq(data.y[data.test_mask]).sum().item())
    acc = correct/int(data.test_mask.sum())
    print(acc)
