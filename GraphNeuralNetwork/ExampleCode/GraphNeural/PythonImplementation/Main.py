import BaseFunctions.IO as IO 
import BaseFunctions.Particle as Particle 
import BaseFunctions.PyGeometric as PyG
import BaseFunctions.Models as M
import torch


# Get the sample directory
directory = "Data/W_to_lepton.root"
Raw_Map = IO.ReadRootFile(directory, 100)
Mapped_Events = Particle.EventMapGenerator(Raw_Map).EventMap
Loader = PyG.Convert_Sample_Object(Mapped_Events)

#M.RunModel(Loader)
M.Run_Model(Loader)


#import ClosureTests.Test_PyGeometric as PyGT
#PyGT.Test_GCN_Net()

