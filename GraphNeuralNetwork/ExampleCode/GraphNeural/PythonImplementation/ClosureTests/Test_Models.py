import BaseFunctions.IO as IO
import BaseFunctions.DataPreparation as DP
import BaseFunctions.Graphs as G
import BaseFunctions.Runners as R
import BaseFunctions.Calculators as C

def Test_EdgeConv():

    Dir = "./Data/W_to_lepton.root"
    Labels, Particles, LabelsPID = DP.RootMapObjects(Dir, 100)
    
    EdgeFeatures = ["dE"]
    NodeFeatures = ["E"]
    Events = []
    for i in Labels:
        P = Particles[i]
        L = Labels[i]
        L_PID = LabelsPID[i]
        Pairs = G.GenerateConnectivity(P)
        Edges = G.DefineEdgeFeatures(P, Pairs, EdgeFeatures)
        Nodes = G.DefineNodeFeatures(P, NodeFeatures)
        Events.append(G.GraphDataObject(Pairs, Nodes, Edges, L, [1, 1, 1]))
    
    Results = R.Run_EdgeConv(Events, 1, 2, True) 
    Topology = C.TopologicalProbabilities(Results)
    for i in Topology:
        n = i[0]
        n_r = i[1]
        P = i[2]
        message = "node: " + str(n) + " -> " + str(n_r) + " P: " + str(P)
        print(message)
    
