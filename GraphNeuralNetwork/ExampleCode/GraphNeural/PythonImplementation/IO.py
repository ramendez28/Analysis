import ROOT 

def PDG_To_String(pdg):
    PDG_dictionary = {}
    
    # Quarks 
    PDG_dictionary[1] = "d"
    PDG_dictionary[-1] = "d~"
    PDG_dictionary[2] = "u"
    PDG_dictionary[-2] = "u~"
    PDG_dictionary[3] = "s"
    PDG_dictionary[-3] = "s~"
    PDG_dictionary[4] = "c"
    PDG_dictionary[-4] = "c~"
    PDG_dictionary[5] = "b"
    PDG_dictionary[-5] = "b~"
    PDG_dictionary[6] = "t"
    PDG_dictionary[-6] = "t~" 
    
    # electron 
    PDG_dictionary[11] = "e-" 
    PDG_dictionary[-11] = "e+"
    PDG_dictionary[12] = "ve"
    PDG_dictionary[-12] = "ve~"
    
    # Muon 
    PDG_dictionary[13] = "mu-" 
    PDG_dictionary[-13] = "mu+" 
    PDG_dictionary[14] = "vmu" 
    PDG_dictionary[-14] = "vmu~"
    
    # ======= Boson 
    PDG_dictionary[24] = "W+" 
    PDG_dictionary[-24] = "W-" 
    PDG_dictionary[23] = "Z0"
    PDG_dictionary[21] = "g"

    return PDG_dictionary[pdg]; 

def ReadRootFile(File):
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
            
            if (Mother1 == Mother2 and Mother1 > 0 and Mother2 > 0):
                Decay_Chains.append([Mother1, Attributes])
            if (Mother1 != Mother2):
                MC_Final_State.append([Mother2, Attributes])
            if (Mother1 == Mother2 and Mother1 < 0 and Mother2 < 0):
                Initializer.append([Mother1, Attributes])

        Temp["Decay_Chains"] = Decay_Chains
        Temp["MC_Final_State"] = MC_Final_State
        Temp["Initial_State"] = Initializer
        Output.append(Temp)

        if i == 100:
            break
    return Output

def VerifyProcess(Data, index):
    Test = Data[index]
    Initial_State = Test["Initial_State"]
    MC_State = Test["MC_Final_State"]
    Decays = Test["Decay_Chains"]

    message = ""
    for i in Initial_State:
        Mother = i[0]
        Attributes = i[1]
        message += PDG_To_String(Attributes["PID"]) 
        message += " "
       
    message += "-> "
    for i in MC_State:
        Mother = i[0]
        Attributes = i[1]
        message += PDG_To_String(Attributes["PID"]) 
        message += " "

    message += "-> "
    for i in Decays:
        Mother = i[0]
        Attributes = i[1]
        message += PDG_To_String(Attributes["PID"]) 
        message += " "
    return message

def CreateFeatureDictionary(Dictionary):
    Output_Map = {}
    Output_Map["WPx"] = []
    Output_Map["WPy"] = []
    Output_Map["WPz"] = []
    Output_Map["WE"] = []
    Output_Map["WM"] = []
    Output_Map["WC"] = []

    Output_Map["ePx"] = []
    Output_Map["ePy"] = []
    Output_Map["ePz"] = []
    Output_Map["eE"] = []
    Output_Map["eM"] = []
    Output_Map["eC"] = []

    Output_Map["vePx"] = []
    Output_Map["vePy"] = []
    Output_Map["vePz"] = []
    Output_Map["veE"] = []
    Output_Map["veM"] = []
    Output_Map["veC"] = []

    # Connectivity Features i.e. the invariant mass and charge 
    # Inv Mass 
    Output_Map["W_e"] = []
    Output_Map["W_ve"] = []
    Output_Map["e_ve"] = []

    # Charge 
    Output_Map["W_e_C"] = []
    Output_Map["W_ve_C"] = []
    Output_Map["e_ve_C"] = []

    x = -1
    for i in Dictionary:
        x = x+1
        process = VerifyProcess(Dictionary, x)
        if "mu+" in process:
            continue 

        Decay_Chain = i["Decay_Chains"]
        MC_Final_State = i["MC_Final_State"]
        Initial_State = i["Initial_State"]

        # The MC Final State has the e+ and ve four momenta 
        # the initial state has the W+
        for ini in Initial_State:
            init = ini[1]
            Output_Map["WPx"].append(init["Px"])
            Output_Map["WPy"].append(init["Py"])
            Output_Map["WPz"].append(init["Pz"])
            Output_Map["WE"].append(init["E"])
            Output_Map["WM"].append(init["M"])
            Output_Map["WC"].append(1)
          
        Temp = []
        for ff in MC_Final_State:
            final = ff[1] 
            
            # Calculate the 4 vector between the init particle and the decay products
            lor = ROOT.TLorentzVector()
            lor.SetPxPyPzE(init["Px"] - final["Px"], init["Py"] - final["Py"], init["Pz"] - final["Pz"], init["E"] - final["E"])

            particle = PDG_To_String(final["PID"])
            if particle == "e+":
                Output_Map["ePx"].append(final["Px"])
                Output_Map["ePy"].append(final["Py"])
                Output_Map["ePz"].append(final["Pz"])
                Output_Map["eE"].append(final["E"])
                Output_Map["eM"].append(final["M"])
                Output_Map["eC"].append(1)
                Output_Map["W_e"].append(lor.M())
                Output_Map["W_e_C"].append(1)
    
            if particle == "ve":
                Output_Map["vePx"].append(final["Px"])
                Output_Map["vePy"].append(final["Py"])
                Output_Map["vePz"].append(final["Pz"])
                Output_Map["veE"].append(final["E"])
                Output_Map["veM"].append(final["M"])
                Output_Map["veC"].append(0) 
                Output_Map["W_ve"].append(lor.M())
                Output_Map["W_ve_C"].append(0)

            Temp.append(final)
        
        lor = ROOT.TLorentzVector()
        lor.SetPxPyPzE(Temp[0]["Px"] + Temp[1]["Px"], Temp[0]["Py"] + Temp[1]["Py"], Temp[0]["Pz"] + Temp[1]["Pz"], Temp[0]["E"] + Temp[1]["E"])
        Output_Map["e_ve"].append(lor.M()) 
        Output_Map["e_ve_C"].append(0)


    return Output_Map



