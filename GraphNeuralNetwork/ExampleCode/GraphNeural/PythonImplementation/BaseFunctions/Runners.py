import BaseFunctions.Calculators as Cal

def Run_EdgeConv(loader):

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
           prob = Cal.CalculateLinkProbability(i, j)
           print(prob)
