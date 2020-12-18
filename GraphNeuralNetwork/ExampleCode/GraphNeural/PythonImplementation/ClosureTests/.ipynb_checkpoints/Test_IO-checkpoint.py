import BaseFunctions.IO as IO
import BaseFunctions.Particle as Particle

def Test_ReadRootFile(Directory):
    print("Running Test_ReadRooFile")
    Map = IO.ReadRootFile(Directory, 1)
    Fail = True
    if len(Map) == 100:
        print("Events... OK")
        Fail = False
    if len(Map) == 100 and "Decay_Chains" in Map[0]:
        print("Decay Chain... OK")
        Fail = False
    if len(Map) == 100 and "MC_Final_State" in Map[0]:
        print("MC Final State... OK")
        Fail = False
    if len(Map) == 100 and "Initial_State" in Map[0]:
        print("Initial State... OK")
        Fail = False

def Test_EventMapGenerator(Directory):
    print("Running Test_EventMapGenerator")
    leng = 5
    Map = IO.ReadRootFile(Directory, leng)
    for i in range(leng):
        Event = Particle.VerifyProcess(Map, i)
        print(Event)
    
    Output = Particle.EventMapGenerator(Map, leng).EventMap
    for i in Output:
        Event = Particle.VerifyProcessObject(Output, i)
        print(Event)
        
        
        

