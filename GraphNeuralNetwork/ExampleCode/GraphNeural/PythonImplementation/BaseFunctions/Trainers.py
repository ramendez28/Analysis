import BaseFunctions.Models as M
import torch

def Train_EdgeConv(model, optimizer, data):
    model.train()
    optimizer.zero_grad()
    x = model(data.x, data.edge_index)
    loss = torch.nn.CrossEntropyLoss()
    l = loss(x[data.mask], data.y[data.mask])
    l.backward()
    optimizer.step()
    return l


