import BaseFunctions.Graphs as G
import BaseFunctions.Particle as P
import BaseFunctions.IO as IO

def ProcessDataSample(EventMap):
    TruthLabels = {}
    TruthParticles = {} 
    for i in EventMap:
        TruthLabels[i] = []
        TruthParticles[i] = []

        p = 0
        for x in EventMap[i]["Initial"]:
            TruthLabels[i].append(p)
            TruthParticles[i].append(x)

        p += 1
        for x in EventMap[i]["Products"]:
            TruthLabels[i].append(p)
            TruthParticles[i].append(x)

        for x in EventMap[i]["Products"]:
            p += 1
            for y in x.Decay:
                TruthLabels[i].append(p)
                TruthParticles[i].append(y)

        for x in EventMap[i]["Products"]:
            for y in x.Decay:
                if len(y.Decay) != 0:
                    p += 1
                for t in y.Decay:
                    TruthLabels[i].append(p)
                    TruthParticles[i].append(t)
 
    return TruthLabels, TruthParticles

def RootMapObjects(Dir, Events = -1):
    Map = IO.ReadRootFile(Dir)
    EventObjects = P.EventMapGenerator(Map, Events).EventMap
    Labels, Particles = ProcessDataSample(EventObjects)
    return Labels, Particles
