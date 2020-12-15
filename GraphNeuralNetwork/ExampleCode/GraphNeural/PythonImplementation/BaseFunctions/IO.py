import ROOT

def ReadRootFile(Directory, Events = -1):
    File = ROOT.TFile(Directory)
    f = File.Get("LHEF")
    Output = []
    for i in range(f.GetEntries()):
        f.GetEntry(i,1)
        E = f.GetLeaf("Event.Number").GetValue(0)
        P_s = f.GetLeaf("Particle_size").GetValue(0)
        Temp = {}
        Decay_Chains = []
        MC_Final_State = []
        Initializer = []
    
        index = 0
        for x in range(int(P_s)):
            Mother1 = f.GetLeaf("Particle.Mother1").GetValue(x)
            Mother2 = f.GetLeaf("Particle.Mother2").GetValue(x)

            Attributes = {}
            Attributes["Px"] = f.GetLeaf("Particle.Px").GetValue(x)
            Attributes["Py"] = f.GetLeaf("Particle.Py").GetValue(x)
            Attributes["Pz"] = f.GetLeaf("Particle.Pz").GetValue(x)
            Attributes["E"] = f.GetLeaf("Particle.E").GetValue(x)
            Attributes["M"] = f.GetLeaf("Particle.M").GetValue(x)
            Attributes["PID"] = f.GetLeaf("Particle.PID").GetValue(x)
            Attributes["Status"] = f.GetLeaf("Particle.Status").GetValue(x)
            Attributes["Mother1"] = Mother1
            Attributes["Mother2"] = Mother2            
            
            if (Mother1 == Mother2 and Mother1 > 0 and Mother2 > 0):
                if Attributes["Status"] == 2.0:
                    Attributes["Decay_Linker"] = index
                else:
                    Attributes["Decay_Linker"] = -1
                Decay_Chains.append([Mother1, Attributes])
            if (Mother1 != Mother2):
                index = index +1
                Attributes["Decay_Linker"] = index
                MC_Final_State.append([Mother2, Attributes])
                
            if (Mother1 == Mother2 and Mother1 < 0 and Mother2 < 0):
                Attributes["Decay_Linker"] = -2
                Initializer.append([Mother1, Attributes])
                
        Temp["Decay_Chains"] = Decay_Chains
        Temp["MC_Final_State"] = MC_Final_State
        Temp["Initial_State"] = Initializer
        Output.append(Temp)

        if i == Events-1 and Events != -1:
            break
    return Output

