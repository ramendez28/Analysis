import torch
import torch.nn as nn
import torch.nn.functional as F

import dgl 
import dgl.nn as dglnn
import dgl.function as fn

import ROOT
import math
import networkx as nx 
import matplotlib.pyplot as plt
import numpy as np

class DotProductPredictor(nn.Module):
  def forward(self, graph, h):
    with graph.local_scope():
      graph.ndata["h"] = h
      graph.apply_edges(fn.u_dot_v("h", "h", "score"))
      return graph.edata["score"]

class MLPPredictor(nn.Module):
  def __init__(self, in_features, out_classes):
    super().__init__()
    self.W = nn.Linear(in_features * 2, out_classes)
  
  def apply_edges(self, edges):
    h_u = edges.src["h"]
    h_v = edges.dst["h"]
    score = self.W(torch.cat([h_u, h_v], 1))
    return {"score": score}

  def forward(self, graph, h):
    with graph.local_scope():
      graph.ndata["h"] = h
      graph.apply_edges(self.apply_edges)
      return graph.edata["score"]

class Model(nn.Module):
  def __init__(self, in_features, hidden_features, out_features):
    super().__init__()
    self.sage = SAGE(in_features, hidden_features, out_features)
    self.pred = DotProductPredictor()
  
  def forward(self, g, neg_g, x):
    h = self.sage(g, x)
    return self.pred(g, h), self.pred(neg_g, h)

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

def construct_negative_graph(graph, k):
  src, dst = graph.edges()

  neg_src = src.repeat_interleave(k)
  neg_dst = torch.randint(0, graph.number_of_nodes(), (len(src)*k, ))
  return dgl.graph((neg_src, neg_dst), num_nodes = graph.number_of_nodes())

def compute_loss(pos_score, neg_score):
  n_edges = pos_score.shape[0]
  return (1-neg_score.view(n_edges, -1) + pos_score.unsqueeze(1)).clamp(min=0).mean()

def InvariantMass(vec1, vec2):
  m_sq_2 = pow(vec1[0] + vec2[0], 2) - pow(vec1[1] - vec2[1], 2) - pow(vec1[2] - vec2[2], 2) - pow(vec1[3] - vec2[3], 2) 
  return math.sqrt(m_sq_2)

f = ROOT.TFile("NTuples/BB_MuMu-evtgen-ntuples.root")
Entries = dict()
Truth = dict()
for i in f.mu:
  event = i.__event__
  Entries[str(event)] = []
  Truth[str(event)] = []

for i in f.B0:
  event = i.__event__
  sig = i.isSignal
  Truth[str(event)].append(sig) 

for i in f.mu:
  event = i.__event__
  px = i.px
  py = i.py
  pz = i.pz
  E = i.E
  PDG = i.mcPDG
  Temp = [E, px, py, pz, PDG]
  Entries[str(event)].append(Temp)

# Convert the data structure to a version that we need 
Mu1_C = []
Mu2_C = []
Mu3_C = []
Mu4_C = []

IM_1_2 = []
IM_1_3 = []
IM_1_4 = []

IM_2_1 = []
IM_2_3 = []
IM_2_4 = []

IM_3_1 = []
IM_3_2 = []
IM_3_4 = []

IM_4_1 = []
IM_4_2 = []
IM_4_3 = []

CxC_1_2 = []
CxC_1_3 = []
CxC_1_4 = []

CxC_2_1 = []
CxC_2_3 = []
CxC_2_4 = []

CxC_3_1 = []
CxC_3_2 = []
CxC_3_4 = []

CxC_4_1 = []
CxC_4_2 = []
CxC_4_3 = []

T_1_2 = []
T_1_3 = []
T_1_4 = []

T_2_1 = []
T_2_3 = []
T_2_4 = []

T_3_1 = []
T_3_2 = []
T_3_4 = []

T_4_1 = []
T_4_2 = []
T_4_3 = []

for key in Entries:
  Event = Entries[key]
  Mu1 = Event[0]
  Mu2 = Event[1]
  Mu3 = Event[2]
  Mu4 = Event[3]
  
  # Append the charges 
  C1 = Mu1[3]/13
  C2 = Mu2[3]/13
  C3 = Mu3[3]/13
  C4 = Mu4[3]/13

  Mu1_C.append(C1)
  Mu2_C.append(C2)
  Mu3_C.append(C3)
  Mu4_C.append(C4)

  # Calculate the invariant mass 
  IM_1_2.append(InvariantMass(Mu1, Mu2)) 
  IM_1_3.append(InvariantMass(Mu1, Mu3))   
  IM_1_4.append(InvariantMass(Mu1, Mu4))  
  
  IM_2_1.append(InvariantMass(Mu2, Mu1))
  IM_2_3.append(InvariantMass(Mu2, Mu3))
  IM_2_4.append(InvariantMass(Mu2, Mu4))

  IM_3_1.append(InvariantMass(Mu3, Mu1)) 
  IM_3_2.append(InvariantMass(Mu3, Mu2))   
  IM_3_4.append(InvariantMass(Mu3, Mu4))  
  
  IM_4_1.append(InvariantMass(Mu4, Mu1))
  IM_4_2.append(InvariantMass(Mu4, Mu2))
  IM_4_3.append(InvariantMass(Mu4, Mu3))

  # Calculate the charge product
  CxC_1_2.append(C1*C2) 
  CxC_1_3.append(C1*C3)   
  CxC_1_4.append(C1*C4)  
                 
  CxC_2_1.append(C2*C1)
  CxC_2_3.append(C2*C3)
  CxC_2_4.append(C2*C4)
                 
  CxC_3_1.append(C3*C1) 
  CxC_3_2.append(C3*C2)   
  CxC_3_4.append(C3*C4)  
                 
  CxC_4_1.append(C4*C1)
  CxC_4_2.append(C4*C2)
  CxC_4_3.append(C4*C3)

  sig = Truth[key]
  T_1_2.append(sig[0]*sig[1])
  T_1_3.append(sig[0]*sig[2])
  T_1_4.append(sig[0]*sig[3])

  T_2_1.append(sig[1]*sig[0])
  T_2_3.append(sig[1]*sig[2])
  T_2_4.append(sig[1]*sig[3])
       
  T_3_1.append(sig[2]*sig[0])
  T_3_2.append(sig[2]*sig[1])
  T_3_4.append(sig[2]*sig[3])
       
  T_4_1.append(sig[3]*sig[0])
  T_4_2.append(sig[3]*sig[1])
  T_4_3.append(sig[3]*sig[2])



# Create the edges: In our case we want -> mu1, mu2, mu3, mu4 so 6 edges we need to create edges for both directions 
u, v = torch.tensor([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]), torch.tensor([1, 2, 3, 0, 2, 3, 0, 1, 3, 0, 1, 2])
g = dgl.graph((u, v))

# Convert the tensor graphs to a bidirectional 
edge_pred_graph = dgl.to_bidirected(g)


# Here (I think) we populate the features of the nodes and edges with the data
edge_pred_graph.ndata["Charge"] = torch.tensor([Mu1_C, Mu2_C, Mu3_C, Mu4_C])
edge_pred_graph.edata["InvMass"] = torch.tensor([IM_1_2, IM_1_3, IM_1_4, IM_2_1, IM_2_3, IM_2_4, IM_3_1, IM_3_2, IM_3_4, IM_4_1, IM_4_2, IM_4_3])
edge_pred_graph.edata["C1xC2"] = torch.tensor([CxC_1_2, CxC_1_3, CxC_1_4, CxC_2_1, CxC_2_3, CxC_2_4, CxC_3_1, CxC_3_2, CxC_3_4, CxC_4_1, CxC_4_2, CxC_4_3])

# Give each edge a label 
edge_pred_graph.edata["label"] = torch.randn(12)

# Here we create the truth sample that will be used to verify the prediction (?)
edge_pred_graph.edata["train_mask"] = torch.tensor([T_1_2, T_1_3, T_1_4, T_2_1, T_2_3, T_2_4, T_3_1, T_3_2, T_3_4, T_4_1, T_4_2, T_4_3])

# Here we basically get back the data since they are stored as a semi dictionary (?)
node_features = edge_pred_graph.ndata["Charge"]
n_features = node_features.shape[1]
k = 1

model = Model(n_features, 12, 12)
opt = torch.optim.Adam(model.parameters())

for epoch in range(1000):
    negative_graph = construct_negative_graph(edge_pred_graph, k)
    pos_score, neg_score = model(edge_pred_graph, negative_graph, node_features)
    loss = compute_loss(pos_score, neg_score)
    opt.zero_grad()
    loss.backward()
    opt.step()
    print(loss.item())

node_embeddings = model.sage(edge_pred_graph, node_features)
print(node_embeddings)

## Lets visualize the graph
#nx_G = edge_pred_graph.to_networkx().to_undirected()
#pos = nx.kamada_kawai_layout(nx_G)
#
#fig = plt.figure()
#fig.canvas.draw()
#plt.show()
#nx.draw(nx_G, pos, with_labels = True)
#plt.draw()
#plt.savefig("lol.png")

