import torch
import BaseFunctions.Models as M
import BaseFunctions.Trainers as T
import torch.nn.functional as F

def Run_EdgeConv(loader, in_channels, out_channels, CUDA = False): 
    if CUDA == True:
        device = torch.device("cuda")
        model = M.EdgeConv(in_channels, out_channels).to(device)
    else: 
        model = M.EdgeConv(in_channels, out_channels)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01, weight_decay = 1e-4)
     
    for epoch in range(300):
        for data in loader:
            if CUDA != False:
                data.to(device)
            loss = T.Train_EdgeConv(model, optimizer, data)
        print(round(float(loss), 5))
        _, y = model(data.x, data.edge_index).max(dim = 1)
        print(y, data.y)

    return model(data.x, data.edge_index)
