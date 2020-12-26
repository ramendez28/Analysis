import BaseFunctions.IO as IO
import BaseFunctions.DataPreparation as DP
import BaseFunctions.Graphs as G

def Test_EdgeConv():

    Dir = "./Data/W_to_lepton.root"
    Labels, Particles = DP.RootMapObjects(Dir, 2)
    
    EdgeFeatures = ["dE"]
    NodeFeatures = ["E"]
    Events = []
    for i in Labels:
        P = Particles[i]
        L = Labels[i]
        Pairs = G.GenerateConnectivity(P)
        
        Nodes = []
        Edges = []
        for p in P: 
            Nodes.append(G.DefineNodeFeatures(p, NodeFeatures))
            Edges.append(G.DefineEdgeFeatures(p, Pairs, EdgeFeatures))
        
        Events.append(Data(Pairs, Nodes, Edges, L))

        
