import torch
import BaseFunctions.Models as M
import BaseFunctions.Trainers as T

def Run_EdgeConv(loader, in_channels, out_channels, CUDA = False): 
    if CUDA == True:
        device = torch.device("cuda")
        model = M.EdgeConv(in_channels, out_channels).to(device)
    else: 
        model = M.EdgeConv(in_channels, out_channels)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01, weight_decay = 1e-5)
     
    for epoch in range(50):
        for data in loader:
            data.to(device)
            loss = T.Train_EdgeConv(model, optimizer, data)

    return model(data.x, data.edge_index)
