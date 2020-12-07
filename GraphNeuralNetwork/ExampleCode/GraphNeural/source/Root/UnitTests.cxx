#include<UnitTests.h>

using namespace TensorConversion;

void TensorTests::TestTensorConversion()
{
  // Example data types
  auto options = torch::TensorOptions().dtype(torch::kFloat32);

  std::vector<std::vector<float>> v_float = {{1,1},{2, 2}};
  torch::Tensor out_v_float = ToTensor(v_float, options);  

  std::vector<float> v_float_1 = {1,1}; 
  torch::Tensor o_float_1 = ToTensor(v_float_1); 
  
  std::cout << o_float_1 << std::endl; // <---- Need to fix this: output if bool but should be float 
}
















void TestGeometricData::TestCreateObject()
{
  // Define the vector representation of the Graph that we will be training 
  std::vector<std::vector<long>> edge_index_v = {{0, 1, 2, 0, 3}, {1, 0, 1, 3, 2}}; 
  std::vector<float> node_targets_v = {0, 1, 0, 1}; 
  std::vector<std::vector<float>> node_features_v = {{2, 1}, {5, 4}, {3, 7}, {12, 0}}; 

  // Convert these representations to PyTorch tensors 
  torch::Tensor edge_index = ToTensor(edge_index_v); 
  torch::Tensor node_targets = ToTensor(node_targets_v); 
  torch::Tensor node_features = ToTensor(node_features_v); 

  GeometricData Data(node_features, edge_index, node_targets); 
  
  Data.CheckObject();



}

