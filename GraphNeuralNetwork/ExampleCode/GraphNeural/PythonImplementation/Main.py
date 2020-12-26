import ClosureTests.Test_IO as IO
import ClosureTests.Test_PyGeometric as PyG
import ClosureTests.Test_Models as M

Dir = "./Data/W_to_lepton.root"
IO.Test_ReadRootFile(Dir)
IO.Test_EventMapGenerator(Dir)

PyG.ClosureData()
PyG.Test_ConnectivitySourceDestination()
PyG.Test_GraphDataObject()

M.Test_EdgeConv()
