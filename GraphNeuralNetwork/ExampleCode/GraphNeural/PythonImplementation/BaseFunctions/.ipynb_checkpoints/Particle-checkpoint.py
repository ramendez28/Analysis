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

class Particle:
    def __init__(self, Map):
        self.Symbol = PDG_To_String(Map["PID"]) 
        self.Charge = Map["PID"]/abs(Map["PID"]) # nEED to fixt this 
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
        def CreateMotherMap(Input, Map):
            for i in Map:
                Input[i[1]["Mother2"]] = []
            return Input
        
        def FillMotherMap(Input, Map):
            for i in Map:
                Input[i[1]["Mother2"]].append(i[1])
            return Input

        
        Decay = self.EventParticles["Decay_Chains"]
        Final = self.EventParticles["MC_Final_State"]
        Init = self.EventParticles["Initial_State"]
        Mother_Dictionary = {}
        Mother_Dictionary = CreateMotherMap(Mother_Dictionary, Init)
        Mother_Dictionary = CreateMotherMap(Mother_Dictionary, Final)
        Mother_Dictionary = CreateMotherMap(Mother_Dictionary, Decay)
        Mother_Dictionary = FillMotherMap(Mother_Dictionary, Init) 
        Mother_Dictionary = FillMotherMap(Mother_Dictionary, Final)         
        Mother_Dictionary = FillMotherMap(Mother_Dictionary, Decay) 

        Decay_Chain_Particles = {}
        Linker = 0
        Decay_Chain_Particles[-1] = Mother_Dictionary[-1]        
        for i in range(len(Mother_Dictionary)-1):
            Particles = Mother_Dictionary[i+1]
            for x in Particles:
                if x["Mother1"] != x["Mother2"]:
                    Decay_Chain_Particles[x["Decay_Linker"]] = []
                    Decay_Chain_Particles[x["Decay_Linker"]].append(x)
                elif x["Decay_Linker"] > 0:
                    Decay_Chain_Particles[x["Decay_Linker"]].append(x)
                    Linker = x["Decay_Linker"]
                elif x["Decay_Linker"] == -1 and Linker != 0:
                    Decay_Chain_Particles[Linker].append(x)
                    
        for i in Decay_Chain_Particles:
            Groups = []
            print("------")
            M = reversed(Decay_Chain_Particles)[0]["Mother1"]
            for x in reversed(Decay_Chain_Particles[i]):
                obj = Particle(x)
                if x["Mother1"] == M:
                    Groups.append(obj)
                elif x["Mother1"] != M and x["Status"] == 2:
                    obj.Decay = Groups
                    Groups = []
                    Groups.append(obj)
                    M = x["Mother1"]
                if x["Mother1"] != M and :
                    
                    
                    
                    