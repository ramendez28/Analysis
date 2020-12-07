#include<PyGeometric_Functions.h>

// Initialize the variables in the object
GeometricData::GeometricData(torch::Tensor node_features, torch::Tensor edge_index, torch::Tensor edge_attributes, torch::Tensor node_targets)
{
  this -> node_features = node_features; 
  this -> edge_index = edge_index; 
  this -> edge_attributes = edge_attributes; 
  this -> node_targets = node_targets; 
}

GeometricData::GeometricData(torch::Tensor node_features, torch::Tensor edge_index, torch::Tensor node_targets)
{
  this -> node_features = node_features; 
  this -> node_targets = node_targets; 
  this -> edge_index = edge_index;
}

GeometricData::GeometricData(int test)
{
  this -> test = test; 
}




void GeometricData::CheckObject()
{
  std::cout << node_features << std::endl;

}


