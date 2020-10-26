import ROOT 

# /////////////////// Here we read the ROOT ntuples //////////////////// #

f = ROOT.TFile("NTuples/BB_MuMu-evtgen-ntuples.root")

# This holds the entries of the muons (Entries) and Truth holds the pair of muons that belong together 
# Muons keeps track of the muon index
Entries = dict()
Truth = dict()
Muons = dict()
Node_label = dict()
Node_feature = dict()
Truth = dict()

# Populate the dictionaries with empty lists for each event 
for i in f.mu:

  Entries[str(i.__event__)] = []
  Truth[str(i.__event__)] = []
  Muons[str(i.__event__)] = []
  Node_label[str(i.__event__)] = []
  Node_feature[str(i.__event__)] = []
  Truth[str(i.__event__)] = []


# Populate the entries with the charge integer (-1 or +1)
# Definition of Muons: B^_0 -> mu1, mu2 (-511) :: B^0 -> mu3, mu4 (511)
in1 = 1
in2 = 3
for i in f.mu:
  Entries[str(i.__event__)].append(int(i.mcPDG/13))
 
  # B^_0  
  if i.genMotherPDG < 0:
    Muons[str(i.__event__)].append(int(in1))
    in1 = in1+1
 
  # B^0 
  if i.genMotherPDG > 0:
    Muons[str(i.__event__)].append(int(in2))
    in2 = in2 + 1

  if in1 == 3 and in2 == 5:
    in1 = 1
    in2 = 3

# Create truth information with the following rule:
# - C1*C2 = -1 -> Signal (1)
# - C1*C2 = +1 -> No Signal (0)
for i in Entries:
  muon_label = Muons[i]
  muon_charge = Entries[i]
  
  for (x, C1) in zip(muon_label, muon_charge):
    for (z, C2) in zip(muon_label, muon_charge):
      if x != z:
        node_label = "mu"+str(x) + "::" + "mu" + str(z)
        Node_label[i].append(node_label)

        C1C2 = C1*C2
        Node_feature[i].append(C1C2)

        if C1C2 < 0:
          sig = 1
        else: 
          sig = 0
        Truth[i].append(sig) 
        
# //////////////////// Create the Graph of system ///////////////////// #
# Define the edges
edges_s = []
edges_r = []

for i in Node_label:
  labels = Node_label[i]
  truth = Truth[i]
  i_s = -1
  for (l_s, t_s) in zip(labels, truth):
    i_s = i_s +1 # Keep track which nodes we are connecting 
    
    i_r = -1
    for (l_r, t_r) in zip(labels, truth):
      i_r = i_r +1 #keep track which nodes we are connecting 
      
      # Make sure each muon in the pair only appears once 
      m_pair1 = l_r.split("::")
      m_pair2 = l_s.split("::")
      
      edges_s.append(i_s)
      edges_r.append(i_r)

  break

# Create the graph object 
import torch
import dgl

u, v = torch.tensor(edges_s), torch.tensor(edges_r)
g = dgl.graph((u, v))
g = dgl.to_bidirected(g)

# Draw the graph using networkx
import networkx as nx
import matplotlib.pyplot as plt

# Plotting stuff 
nx_g = g.to_networkx().to_undirected()
pos = nx.spring_layout(nx_g, seed = 1)
plt.figure(figsize = (8, 8))
plt.axis('off')
nx.draw_networkx(nx_g, pos = pos, node_size=50, cmap = plt.get_cmap("coolwarm"), node_color = torch.tensor(truth), edge_color = 'k', arrows = False, with_labels = True)
plt.savefig("network.png")

# /////////////////////////// The GNN implementation //////////////////////////////// #

import dgl.nn as dglnn 
import torch.nn as nn
import torch.nn.functional as F

class SAGE(nn.Module):
  def __init__(self, in_feats, hid_feats, out_feats):
    super().__init__()
    self.conv1 = dglnn.SAGEConv(in_feats = in_feats, out_feats = hid_feats, aggregator_type = "mean")
    self.conv2 = dglnn.SAGEConv(in_feats = hid_feats, out_feats = out_feats, aggregator_type = "mean")

  def forward(self, graph, inputs):
    h = self.conv1(graph, inputs)
    h = F.relu(h)
    h = self.conv2(graph, h)
    return h

def evaluate(model, graph, features, labels, mask):
  model.eval()
  with torch.no_grad():
    logits = model(graph, features)
    logits = logits[mask]
    labels = labels[mask]
    _, indices = torch.max(logits, dim=1)
    correct = torch.sum(indices == labels)
    return correct.item()*1.0 / len(labels), indices


# ///////////////////////////// Prepare the data ////////////////////////////////////////// #
Masks = dict()
for i in Node_feature:
  node_features = []
  truth_labels = []
  Masks[i] = []

  for x in Node_feature[i]:
    node_features.append([float(x)])
  Node_feature[i] = torch.tensor(node_features)
 
  for x in Truth[i]:
    truth_labels.append(x)
    Masks[i].append(True)
  Masks[i] = torch.tensor(Masks[i])
  Truth[i] = torch.tensor(truth_labels)

# Little explanation here: The Mask variable basically decides which portion of data will be visible to the training. So for example if I have an array [1,2,3,4,5,6] and a mask [true, true, false, false, false, false] I will get [1,2] after applying the mask. In my code this mask is redundant because we are going BY EVENT and each event is considered unrelated i.e. no relational bias. 

# /////////////////////////// Train the model /////////////////////////////////////// #
model = SAGE(in_feats = 1, hid_feats = 2, out_feats = 2)
opt = torch.optim.Adam(model.parameters())

model.train()
for epoch in range(10000):
  node_features = Node_feature[str(epoch+1)]
  node_labels = Truth[str(epoch+1)]
  mask = Masks[str(epoch+1)]

  logits = model(g, node_features)
  loss = F.cross_entropy(logits[mask], node_labels[mask])
  acc, out = evaluate(model, g, node_features, node_labels, mask)
  opt.zero_grad()
  loss.backward()
  opt.step()

  print(out, Truth[str(epoch+1)])

## //////////////////////////////// Debug /////////////////////////////////////////////#
#import dgl.data
#graph = dgl.data.CiteseerGraphDataset()[0]
#node_features = graph.ndata["feat"]
#node_labels = graph.ndata["label"]
#train_mask = graph.ndata["train_mask"]
#valid_mask = graph.ndata["val_mask"]
#test_mask = graph.ndata["test_mask"]
#n_features = node_features.shape[1]
#n_labels = int(node_labels.max().item() +1)
#
#print(node_features, len(node_features))
#print(Node_feature[str(1)], len(Node_feature[str(1)]))
#print(n_features)



#model = SAGE(in_feats = n_features, hid_feats = 100, out_feats = n_labels)
#opt = torch.optim.Adam(model.parameters())
#
#for epoch in range(100):
#  model.train()
#  
#  logits = model(graph, node_features)
#
#  loss = F.cross_entropy(logits[train_mask], node_labels[train_mask])
#
#  acc = evaluate(model, graph, node_features, node_labels, valid_mask)
#
#  opt.zero_grad()
#  loss.backward()
#  opt.step()
#
#  print(loss.item())


