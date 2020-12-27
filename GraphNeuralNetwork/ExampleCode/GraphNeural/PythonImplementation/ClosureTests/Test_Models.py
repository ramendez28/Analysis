import BaseFunctions.IO as IO
import BaseFunctions.DataPreparation as DP
import BaseFunctions.Graphs as G
import BaseFunctions.Runners as R
import BaseFunctions.Calculators as C

# Goal of this test is to illustrate that given the decay process 
# W+ -> e+ ve and the interconnection between all the particles, it
# is possible to show a decay in edges and isolate W+ from e+ ve
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

# This test illustrates that for the decay of W+(-) into muon and electron 
# it is possible to have decaying edges between muons and electrons. This 
# indicates that the GNN can correctly identify nodes originating from the 
# same parent particle.
def Test_MassDifferentiation():
    
    Dir = "./Data/ExampleMC4Tops.root"
    Labels, Particles, LabelsPID = DP.RootMapObjects(Dir, 100)
   
    Allowed_Final = ["mu+", "vmu", "e+", "ve"]
    EdgeFeatures = ["dE", "dPx", "dPy", "dPz"]
    NodeFeatures = ["E", "Px", "Py", "Pz"]
    Events = []
    for i in Labels:
        P = Particles[i]
        L = Labels[i]
        L_PID = LabelsPID[i]

        string = ""
        Part = []
        Labe = []
        Mask = []
        for p, l in zip(P, L):
            if p.Symbol not in Allowed_Final:
                continue 

            Part.append(p)
            Labe.append(l)
            Mask.append(1)
            string = string + p.Symbol + "(" + str(l) + ") "
        if string not in "e+(6) ve(6) mu+(8) vmu(8) ":
            continue


        Pairs = G.GenerateConnectivity(Part)
        Edges = G.DefineEdgeFeatures(Part, Pairs, EdgeFeatures)
        Nodes = G.DefineNodeFeatures(Part, NodeFeatures)
        Events.append(G.GraphDataObject(Pairs, Nodes, Edges, Labe, Mask))
  
    print("Events:")
    print(len(Events))
    Results = R.Run_EdgeConv(Events, len(EdgeFeatures), 10, True)
    Topology = C.TopologicalProbabilities(Results)
    for i in Topology:
        n = i[0]
        n_r = i[1]
        P = i[2]
        message = "node: " + str(n) + " -> " + str(n_r) + " P: " + str(P)
        print(message)

   



