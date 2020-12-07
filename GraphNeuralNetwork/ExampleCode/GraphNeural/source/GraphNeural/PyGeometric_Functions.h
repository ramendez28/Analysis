#ifndef PYGEOMETRIC_FUNCTIONS_H
#define PYGEOMETRIC_FUNCTIONS_H
#include<torch/torch.h>
#include<iostream> 

class GeometricData 
{
  public:
    torch::Tensor node_features; 
    torch::Tensor edge_index; 
    torch::Tensor edge_attributes; 
    torch::Tensor node_targets; 
    int test; 

    GeometricData(torch::Tensor node_features, torch::Tensor edge_index, torch::Tensor edge_attributes, torch::Tensor node_targets); 
    GeometricData(torch::Tensor node_features, torch::Tensor edge_index, torch::Tensor node_targets); 
    GeometricData(int test); 
    void CheckObject(); 
    

    ~GeometricData(){std::cout << "in destructor" << std::endl;}
  
  private:
    




};


#endif 
