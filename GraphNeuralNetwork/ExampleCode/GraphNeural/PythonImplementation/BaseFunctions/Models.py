import torch
from torch_geometric.nn import GCNConv
import torch.nn.functional as F
import BaseFunctions.PyGeometric as PyG

class GCN_Net(torch.nn.Module):
    def __init__(self, Data, hidden_channels):
        super(GCN_Net, self).__init__()

        self.Node_Features = Data.num_features
        self.classes = int(Data.y.max())+ 1
        self.conv1 = GCNConv(self.Node_Features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, self.classes)

    def forward(self, data):
        x = self.conv1(data.x, data.edge_index)
        x = F.relu(x)
        x = self.conv2(x, data.edge_index)
        return F.log_softmax(x, dim=1)

def train(model, optimizer, data):
    model.train()
    optimizer.zero_grad()
    out = model(data)
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()
    return loss

def RunModel(loader):
    model = GCN_Net(loader[0], 4)
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01, weight_decay = 1e-5)
    for epoch in range(200):
        for data in loader:
            data.train_mask = torch.tensor([1, 1, 1], dtype = torch.bool)
            loss = train(model, optimizer, data)
        print(model(data).argmax(dim = 1))


from torch.nn import Sequential as Seq, Linear, ReLU
from torch_geometric.nn import MessagePassing

class EdgeConv(MessagePassing):
    
    def __init__(self, in_channels, out_channels):
        super(EdgeConv, self).__init__(aggr = "mean")
        self.mlp = Seq(Linear(2 * in_channels, out_channels), ReLU(), Linear(out_channels, out_channels))

    def forward(self, x, edge_index):
        return self.propagate(edge_index, x = x)

    def message(self, x_i, x_j):
        tmp = torch.cat([x_i, x_j - x_i], dim = 1)
        return self.mlp(tmp)

    def update(self, aggr_out):
        F.normalize(aggr_out)
        return aggr_out




def Train_EdgeConv(model, optimizer, data):
    optimizer.zero_grad()
    x = model(data.x, data.edge_index)
    loss = torch.nn.CrossEntropyLoss()
    l = loss(x[data.train_mask], data.y[data.train_mask])
    l.backward()
    optimizer.step()
    return loss

import time

def Run_Model(loader):

    model = EdgeConv(1, 2)
    model.train()
    
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01, weight_decay = 1e-5)
    
    for epoch in range(100):
        for data in loader:
            data.train_mask = torch.tensor([1, 1, 1], dtype = torch.bool)
            loss = Train_EdgeConv(model, optimizer, data)

    nodes = model(data.x, data.edge_index)
    print(nodes)
    print(data.x)
    
    for i in nodes:
        print("=======") 
        print(i)
        for j in nodes:
           prob = PyG.CalculateLinkProbability(i, j)
           print(prob)
