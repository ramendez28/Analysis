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
    PDG_dictionary[22] = "gamma"
    PDG_dictionary[25] = "H"

    return PDG_dictionary[pdg]; 

def PDG_To_Charge(pdg):
    PDG_dictionary = {}
    
    # Quarks 
    PDG_dictionary[1] = -1/3
    PDG_dictionary[-1] = 1/3
    PDG_dictionary[2] = 2/3
    PDG_dictionary[-2] = -2/3
    PDG_dictionary[3] = -1/3
    PDG_dictionary[-3] = 1/3
    PDG_dictionary[4] = 2/3
    PDG_dictionary[-4] = -2/3
    PDG_dictionary[5] = -1/3
    PDG_dictionary[-5] = 1/3
    PDG_dictionary[6] = 2/3
    PDG_dictionary[-6] = -2/3 
    
    # electron 
    PDG_dictionary[11] = -1 
    PDG_dictionary[-11] = 1
    PDG_dictionary[12] = 0
    PDG_dictionary[-12] = 0
    
    # Muon 
    PDG_dictionary[13] = -1 
    PDG_dictionary[-13] = 1 
    PDG_dictionary[14] = 0 
    PDG_dictionary[-14] = 0
    
    # ======= Boson 
    PDG_dictionary[24] = +1 
    PDG_dictionary[-24] = -1 
    PDG_dictionary[23] = 0
    PDG_dictionary[21] = 0
    PDG_dictionary[22] = 0
    PDG_dictionary[25] = 0
    
    return PDG_dictionary[pdg]

def VerifyProcess(Data, index):
    def GenerateMessage(message, State):
        if message != "" and len(State) != 0:
            message += "-> "

        for i in State:
            Mother = i[0]
            Attributes = i[1]
            message += PDG_To_String(Attributes["PID"]) 
            message += " "
        return message
    
    
    Test = Data[index]
    Initial_State = Test["Initial_State"]
    MC_State = Test["MC_Final_State"]
    Decays = Test["Decay_Chains"]
    
    message = ""
    message = GenerateMessage(message, Initial_State)
    message = GenerateMessage(message, MC_State)
    message = GenerateMessage(message, Decays)
    return message

def VerifyProcessObject(Data, index):
    init = Data[index]["Initial"]
    prod = Data[index]["Products"]
    string = ""
    for i in init:
        string = string + " " + i.Symbol

    string = string + "-> "
    for i in prod:
        string = string + " " + i.Symbol

    for i in prod:
        string = string + ";"
        for p in i.Decay:
            string = string +" (" + i.Symbol  + " -> "
            string = string + p.Symbol +" "
            if len(p.Decay)!= 0:
                string = string + "-> "
            for x in p.Decay:
                string = string + " " + x.Symbol
            string = string + ")"
        
        
    return string 

class Particle:
    def __init__(self, Map):
        self.Symbol = PDG_To_String(Map["PID"]) 
        self.Charge = PDG_To_Charge(Map["PID"])
        self.Px = Map["Px"]
        self.Py = Map["Py"]
        self.Pz = Map["Pz"]
        self.Energy = Map["E"]
        self.Mass = Map["M"]
        self.PID = Map["PID"]
        self.Decay = []

class EventMapGenerator:
    def __init__(self, Map, Event = -1):
        self.Map = Map
        self.EventMap = {}
        if Event == -1:
            self.Event = len(Map)
        else:
            self.Event = Event
        self.IterateMap()
    
    def IterateMap(self):
        for i in range(len(self.Map)):
            if i+1 > self.Event:
                break
            self.EventParticles = self.Map[i]
            self.EventMap[i+1] = self.CreateParticlesInEvent()
            
    def CreateParticlesInEvent(self):
        Initial = self.EventParticles["Initial_State"]
        MC_Final = self.EventParticles["MC_Final_State"]
        Decay = self.EventParticles["Decay_Chains"]
        
        Output = {}
        Output["Initial"] = []
        Output["Products"] = []
        for i in Initial:
            Output["Initial"].append(Particle(i[1]))
        
        To_Decay = {}
        for i in MC_Final:
            if i[1]["Status"] != 1:
                To_Decay[i[1]["Decay_Linker"]] = Particle(i[1])
            else:
                Output["Products"].append(Particle(i[1]))

        for i in Decay:
            if i[1]["Decay_Linker"] in To_Decay:
                Mother = i[1]["Mother1"]
                P = Particle(i[1])
                Pair = [P]
                P_P = To_Decay[i[1]["Decay_Linker"]]
                for x in Decay:                    
                    if Mother +1 == x[1]["Mother2"] and x[1]["Status"] == 1:
                        P.Decay.append(Particle(x[1]))
                    elif Mother == x[1]["Mother2"] and x[1]["Status"] == 1:
                        Pair.append(Particle(x[1]))
                P_P.Decay = Pair
                Output["Products"].append(P_P)        
        
        return Output
                        
                    
            
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
#     def CreateParticlesInEvent(self):  
#         def CreateMotherMap(Input, Map):
#             for i in Map:
#                 Input[i[1]["Mother2"]] = []
#             return Input
        
#         def FillMotherMap(Input, Map):
#             for i in Map:
#                 Input[i[1]["Mother2"]].append(i[1])
#             return Input

        
#         Decay = self.EventParticles["Decay_Chains"]
#         Final = self.EventParticles["MC_Final_State"]
#         Init = self.EventParticles["Initial_State"]
#         Mother_Dictionary = {}
#         Mother_Dictionary = CreateMotherMap(Mother_Dictionary, Init)
#         Mother_Dictionary = CreateMotherMap(Mother_Dictionary, Final)
#         Mother_Dictionary = CreateMotherMap(Mother_Dictionary, Decay)
#         Mother_Dictionary = FillMotherMap(Mother_Dictionary, Init) 
#         Mother_Dictionary = FillMotherMap(Mother_Dictionary, Final)         
#         Mother_Dictionary = FillMotherMap(Mother_Dictionary, Decay) 

#         Decay_Chain_Particles = {}
#         Linker = 0
#         Decay_Chain_Particles[-1] = Mother_Dictionary[-1]
#         print(Mother_Dictionary)
#         for i in range(len(Mother_Dictionary)-1):
#             Particles = Mother_Dictionary[i+1]
#             for x in Particles:
#                 if x["Mother1"] != x["Mother2"]:
#                     Decay_Chain_Particles[x["Decay_Linker"]] = []
#                     Decay_Chain_Particles[x["Decay_Linker"]].append(x)
#                 elif x["Decay_Linker"] > 0:
#                     Decay_Chain_Particles[x["Decay_Linker"]].append(x)
#                     Linker = x["Decay_Linker"]
#                 elif x["Decay_Linker"] == -1 and Linker != 0:
#                     Decay_Chain_Particles[Linker].append(x)
#                 print(x)
        
#         Output = {}
#         Output["Initial"] = []
#         Output["Products"] = []
#         for i in Decay_Chain_Particles:
#             Groups = {}
#             Groups["Final"] = []
#             Groups["Decay"] = []
#             Groups["MC"] = []
#             for x in Decay_Chain_Particles[i]:
#                 if x["Status"] == 1 and x["Mother1"] == x["Mother2"]:
#                     Groups["Final"].append(x)
                
#                 elif x["Status"] == 2 and x["Mother1"] == x["Mother2"]:
#                     Groups["Decay"].append(x)
            
#                 elif x["Status"] == 2 and x["Mother1"] != x["Mother2"]:
#                     Groups["MC"].append(Particle(x))
            
#                 elif x["Status"] == 1 and x["Mother1"] != x["Mother2"]:
#                     Output["MC"][0].Decay.append(Particle(x))
            
#                 elif x["Status"] == -1:
#                     Output["Initial"].append(Particle(x))
            
#             Chains = []
#             for x in Groups["Decay"]:
#                 if x["Mother1"] == x["Mother2"]:
#                     decay_pairs = []
#                     pairs = []
#                     for p in Groups["Final"]:
#                         if p["Mother2"] == x["Mother2"] +1:
#                             decay_pairs.append(p)
#                         elif p["Mother2"] == x["Mother2"]:
#                             pairs.append(p)
                    
#                     P = Particle(x)                   
#                     for p in decay_pairs:
#                         P.Decay.append(Particle(p))
                        
#                     for p in pairs:
#                         Chains.append(Particle(p))
#                     Chains.append(P)
            
            
#             if len(Chains) == 0:
#                 continue 
                
#             Groups["MC"][0].Decay = Chains
            
            
#             Output["Products"].append(Groups["MC"][0])
#         return Output
