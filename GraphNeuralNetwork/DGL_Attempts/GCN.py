import dgl
import dgl.function as fn 
import torch as th
import torch.nn as nn
import torch.nn.functional as F
from dgl import DGLGraph
import torch

from dgl.data import citation_graph as citegrh
import networkx as nx
import time 
import numpy as np

import ROOT
import math
import matplotlib.pyplot as plt


# //////////////////////////// These are the classes of the GNN /////////////////////////// #
gcn_msg = fn.copy_src(src = "h", out = "m"); 
gcn_reduce = fn.sum(msg = "m", out = "h"); 

def load_cora_data():
  data = citegrh.load_cora()
  features = th.FloatTensor(data.features)
  labels = th.LongTensor(data.labels)
  train_mask = th.BoolTensor(data.train_mask)
  test_mask = th.BoolTensor(data.test_mask)
  g = DGLGraph(data.graph)
  return g, features, labels, train_mask, test_mask

def evaluate(model, g, features, labels, mask):
  model.eval()
  with th.no_grad():
    logits = model(g, features)
    logits = logits[mask]
    labels = labels[mask]
    _, indices = th.max(logits, dim=1)
    print(indices) 
    correct = th.sum(indices == labels)
    return correct.item()*1.0 / len(labels)

class GCNLayer(nn.Module):
  def __init__(self, in_feats, out_feats):
    super(GCNLayer, self).__init__()
    self.linear = nn.Linear(in_feats, out_feats)

  def forward(self, g, feature):
    with g.local_scope():
      g.ndata["h"] = feature
      g.update_all(gcn_msg, gcn_reduce)
      h = g.ndata["h"]
      return self.linear(h)

class Net(nn.Module):
  def __init__(self):
    super(Net, self).__init__()
    self.layer1 = GCNLayer(2, 2)
    self.layer2 = GCNLayer(2, 2)

  def forward(self, g, features):
    x = F.relu(self.layer1(g, features))
    x = self.layer2(g, x)
    return x

def InvariantMass(vec1, vec2):
  m_sq_2 = pow(vec1[0] + vec2[0], 2) - pow(vec1[1] - vec2[1], 2) - pow(vec1[2] - vec2[2], 2) - pow(vec1[3] - vec2[3], 2) 
  return math.sqrt(m_sq_2)

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

# ///////////////////////////// Prepare the data ////////////////////////////////////////// #
Masks = dict()
for i in Node_feature:
  node_features = []
  truth_labels = []
  Masks[i] = []

  for x in Node_feature[i]:
    node_features.append([float(x), float(x)])
  Node_feature[i] = torch.tensor(node_features)
 
  for x in Truth[i]:
    truth_labels.append(x)
    Masks[i].append(True)
  Masks[i] = torch.tensor(Masks[i])
  Truth[i] = torch.tensor(truth_labels)

# Little explanation here: The Mask variable basically decides which portion of data will be visible to the training. So for example if I have an array [1,2,3,4,5,6] and a mask [true, true, false, false, false, false] I will get [1,2] after applying the mask. In my code this mask is redundant because we are going BY EVENT and each event is considered unrelated i.e. no relational bias. 




# //////////////////////// Train the GNN //////////////////// #
net = Net()
net.train()
optimizer = th.optim.Adam(net.parameters(), lr = 1)

for epoch in range(1000):
  logits = net(g, Node_feature[str(epoch+1)])
  _, indices = th.max(logits, dim=1)
  logp = F.log_softmax(logits, 1)
  loss = F.nll_loss(logp, Truth[i])

  optimizer.zero_grad()
  loss.backward()
  optimizer.step()

  acc = evaluate(net, g, Node_feature[str(epoch+1)], Truth[str(epoch+1)], Masks[str(epoch+1)])
  print("Epoch {:05d} | Loss {:.4f} | Test Acc {:.4f}".format(epoch, loss.item(), acc))







# //////////////////////// Train the network //////////////////// #
# Define the network
#net = Net()
#net.train()
#optimizer = th.optim.Adam(net.parameters(), lr = 1)
#
#training = 100
#for epoch in range(10):
#  x = 0; 
#  for i in Entries:
#    if x <= training:
#      logits = net(g, Entries[i][0])
#
#      _, indices = th.max(logits, dim=1)
#      logp = F.log_softmax(logits, 1)
#      loss = F.nll_loss(logp, Entries[i][1])
#
#      optimizer.zero_grad()
#      loss.backward()
#      optimizer.step()
#
#    acc = evaluate(net, g, Entries[i][0], Entries[i][1], Entries[i][2])
#    print("Epoch {:05d} | Loss {:.4f} | Test Acc {:.4f}".format(epoch, loss.item(), acc))
#    
#    if x == training:
#      break;
#    x = x+1

