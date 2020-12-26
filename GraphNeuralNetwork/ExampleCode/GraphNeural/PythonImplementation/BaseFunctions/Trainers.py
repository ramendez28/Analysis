import BaseFunctions.Models as M

def Train_EdgeConv(model, optimizer, data):
    model.train()
    optimizer.zero_grad()
    x = model(data.x, data.edge_index)
    loss = torch.nn.CrossEntropyLoss()
    l = loss(x[data.train_mask], data.y[data.train_mask])
    l.backward()
    optimizer.step()
    return loss


