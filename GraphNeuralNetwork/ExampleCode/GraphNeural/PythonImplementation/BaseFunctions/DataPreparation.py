import BaseFunctions.Graphs as G
import BaseFunctions.Particle as P
import BaseFunctions.IO as IO
from collections import defaultdict

def ProcessDataSample(EventMap):
    TruthLabels = {}
    TruthParticles = {} 
    LabelsPID = {}
    for i in EventMap:
        TruthLabels[i] = []
        TruthParticles[i] = []
        LabelsPID[i] = defaultdict(list)
        p = 0
        for x in EventMap[i]["Initial"]:
            TruthLabels[i].append(p)
            TruthParticles[i].append(x)
            LabelsPID[i][p].append(x.PID)  

        p += 1
        for x in EventMap[i]["Products"]:
            TruthLabels[i].append(p)
            TruthParticles[i].append(x)
            LabelsPID[i][p].append(x.PID)  

        for x in EventMap[i]["Products"]:
            p += 1
            for y in x.Decay:
                TruthLabels[i].append(p)
                TruthParticles[i].append(y)
                LabelsPID[i][p].append(y.PID)  

        for x in EventMap[i]["Products"]:
            for y in x.Decay:
                if len(y.Decay) != 0:
                    p += 1
                for t in y.Decay:
                    TruthLabels[i].append(p)
                    TruthParticles[i].append(t)
                    LabelsPID[i][p].append(t.PID)  

    return TruthLabels, TruthParticles, LabelsPID

def RootMapObjects(Dir, Events = -1):
    Map = IO.ReadRootFile(Dir)
    EventObjects = P.EventMapGenerator(Map, Events).EventMap
    Labels, Particles, LabelsPID = ProcessDataSample(EventObjects)
    return Labels, Particles, LabelsPID
