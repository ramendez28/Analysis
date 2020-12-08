import IO
import ROOT
import torch
from torch_geometric.data import Data, DataLoader 
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import dgl
import PyGeometric_Function as PF

# Get the data in a dictionary format

f = ROOT.TFile("../data/W_to_lepton.root")
Particle_Maps = IO.ReadRootFile(f)
IO.VerifyProcess(Particle_Maps, 0)
Map = IO.CreateFeatureDictionary(Particle_Maps)


# Define the graph structure. In this example we want to 
# see if we can recover the fact that W and e+ ve are 
# connected but not e+ ve

# Completely interconnected graph structure 
edge_index = torch.tensor([[0, 0, 1, 1, 2, 2], [1, 2, 0, 2, 0, 1]], dtype = torch.long)

data_list = []

#for i in range(len(Map["WPx"])):
#    # Create the tensors of the individual features
#    # Node features
#    W_Node = [Map["WPx"][i], Map["WPy"][i], Map["WPz"][i], Map["WE"][i], Map["WM"][i], Map["WC"][i]]
#
#    e_Node = [Map["ePx"][i], Map["ePy"][i], Map["ePz"][i], Map["eE"][i], Map["eM"][i], Map["eC"][i]]
#    ve_Node = [Map["vePx"][i], Map["vePy"][i], Map["vePz"][i], Map["veE"][i], Map["veM"][i], Map["veC"][i]]
#    
#    # Edge features 
#    W_e = [Map["W_e"][i], Map["W_e_C"][i]]
#    W_ve = [Map["W_ve"][i], Map["W_ve_C"][i]]
#    e_ve = [Map["e_ve"][i], Map["e_ve_C"][i]]
#    
#    Node_feat = torch.tensor([W_Node, e_Node, ve_Node], dtype = torch.float)
#    Edge_feat = torch.tensor([W_e, W_ve, W_e, e_ve, W_ve, e_ve], dtype = torch.float) 
#
#    data_list.append([W_Node, e_Node, ve_Node])


#    data = Data(x = Node_feat, edge_index = edge_index, edge_attr = Edge_feat)
#    data_list.append(data)
#
#loader = DataLoader(data_list, batch_size = 32)

# Creating a graphical version of the model 
#edges_raw = edge_index.numpy()
#edges = [(x,y) for x, y in zip(edges_raw[0, :], edges_raw[1, :])]

#G = nx.Graph()
#G.add_nodes_from(list(range(np.max(edges_raw))))
#G.add_edges_from(edges)

nxg = nx.DiGraph()
nxg.add_node(0, id = 0, n1 = Map["WPx"], n2 = Map["WPy"], n3 = Map["WPz"], n4 =  Map["WE"], n5 = Map["WM"], n6 = Map["WC"])
nxg.add_node(1, id = 1, n1 = Map["ePx"], n2 = Map["ePy"], n3 = Map["ePz"], n4 =  Map["eE"], n5 = Map["eM"], n6 = Map["eC"])
nxg.add_node(2, id = 2, n1 = Map["vePx"], n2 = Map["vePy"], n3 = Map["vePz"], n4 =  Map["veE"], n5 = Map["veM"], n6 = Map["veC"])
nxg.add_edge(0, 1, id=0, e1 = Map["W_e"], e2 = Map["W_e_C"])
nxg.add_edge(0, 2, id=0, e1 = Map["W_ve"], e2 = Map["W_ve_C"])
nxg.add_edge(1, 0, id=1, e1 = Map["W_e"], e2 = Map["W_e_C"])
nxg.add_edge(1, 2, id=1, e1 = Map["e_ve"], e2 = Map["e_ve_C"])
nxg.add_edge(2, 0, id=2, e1 = Map["W_ve"], e2 = Map["W_ve_C"])
nxg.add_edge(2, 1, id=2, e1 = Map["e_ve"], e2 = Map["e_ve_C"])
G = dgl.from_networkx(nxg, edge_attrs = ["e1", "e2"], node_attrs = ["n5", "n6"])
G.edata["train_mask"] = torch.zeros(6, dtype = torch.bool).bernoulli(0.6)

node_features = G.ndata["n6"]
train_mask = G.edata["e2"]
model = PF.Model(1, 1, 1)
opt = torch.optim.Adam(model.parameters())

for epoch in range(10):
    pred = model(G, node_features)
    opt.zero_grad()
    opt.step()
    print(pred)






#plt.subplot(111)
#options = {'node_size' : 30, 'width' : 0.2, }
#nx.draw(nxg, **options)
#plt.show()
