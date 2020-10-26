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
    self.layer1 = GCNLayer(1, 1)
    self.layer2 = GCNLayer(1, 1)

  def forward(self, g, features):
    x = F.relu(self.layer1(g, features))
    x = self.layer2(g, x)
    return x

def InvariantMass(vec1, vec2):
  m_sq_2 = pow(vec1[0] + vec2[0], 2) - pow(vec1[1] - vec2[1], 2) - pow(vec1[2] - vec2[2], 2) - pow(vec1[3] - vec2[3], 2) 
  return math.sqrt(m_sq_2)

# //////////////// Generate the graph we are training //////////////////// #
# Generate the nodes 
nodes = []
index = 0
for i in range(4):
  for y in range(4):
    if (i != y):
      nodes.append(index)
      index = index + 1

# Generate the edges we are connecting 
edges_s = []
edges_r = []
for i in range(len(nodes)):
  for y in range(len(nodes)):
    edges_s.append(i)
    edges_r.append(y)

# Create the graph 
u, v = torch.tensor(edges_s), torch.tensor(edges_r)
g = dgl.graph((u, v))
g = dgl.to_bidirected(g)
g.ndata["label"] = torch.tensor(nodes)

# Output the graph 
nx_g = g.to_networkx().to_undirected()
pos = nx.kamada_kawai_layout(nx_g)
fig = plt.figure()
fig.canvas.draw()
nx.draw(nx_g, pos, with_labels = True)
plt.draw()
plt.savefig("network.png")

# ///////////////// Generate the dataset ////////////////////////// #
# Read the events of the root file
f = ROOT.TFile("NTuples/BB_MuMu-evtgen-ntuples.root")
Entries = dict()
Truth = dict()
for i in f.mu:
  event = i.__event__
  Entries[str(event)] = []
  Truth[str(event)] = []

# Read the B0 tree and get the signal muon index 
for i in f.B0:
  event = i.__event__
  sig = i.isSignal
  Truth[str(event)].append(sig) 

# Read the mu tree and get the kinematic entries
for i in f.mu:
  event = i.__event__
  px = i.px
  py = i.py
  pz = i.pz
  E = i.E
  PDG = i.mcPDG/13
  Temp = [E, px, py, pz, PDG]
  Entries[str(event)].append(Temp)

# Calculate the node features (InvMass, Charge) for all events
for i in Entries:
  event = Entries[i]
  truth = Truth[i]
  feature = []
  signals = []
  mask = []
  for x in range(4):
    for y in range(4):
      if (x!=y):
        #feature.append([InvariantMass(event[x], event[y]), event[x][4]*event[y][4]]) 
        Charge = event[x][4]*event[y][4]
        if Charge == -1:
          signals.append(1)
        else:
          signals.append(0)

        feature.append([Charge])
        mask.append(True)

  #print(torch.tensor(feature))
  Entries[i] = [torch.tensor(feature), torch.tensor(signals), torch.tensor(mask)]

# //////////////////////// Train the network //////////////////// #
# Define the network
net = Net()
net.train()
optimizer = th.optim.Adam(net.parameters(), lr = 1)

training = 100
for epoch in range(10):
  x = 0; 
  for i in Entries:
    if x <= training:
      logits = net(g, Entries[i][0])

      _, indices = th.max(logits, dim=1)
      logp = F.log_softmax(logits, 1)
      loss = F.nll_loss(logp, Entries[i][1])

      optimizer.zero_grad()
      loss.backward()
      optimizer.step()

    acc = evaluate(net, g, Entries[i][0], Entries[i][1], Entries[i][2])
    print("Epoch {:05d} | Loss {:.4f} | Test Acc {:.4f}".format(epoch, loss.item(), acc))
    
    if x == training:
      break;
    x = x+1

