#ifndef PYTORCH_FUNCTIONS_H
#define PYTORCH_FUNCTIONS_H
#include<torch/torch.h>
#include<iostream>


namespace TensorConversion
{

  template<typename T>
  torch::Tensor ToTensor(std::vector<std::vector<T>> vec, torch::TensorOptions options)
  {
    T array[vec.size()][vec[0].size()]; 
    for (int i(0); i < vec.size(); i++)
    {
      for (int j(0); j < vec.at(i).size(); j++){array[i][j] = vec.at(i).at(j); }
    }
    return torch::tensor(array, options); 
  }

  template<typename T>
  torch::Tensor ToTensor(std::vector<std::vector<T>> vec)
  {
    T array[vec.size()][vec[0].size()]; 
    for (int i(0); i < vec.size(); i++)
    {
      for (int j(0); j < vec.at(i).size(); j++){array[i][j] = vec.at(i).at(j); }
    }
    return torch::tensor(array); 
  }

  template<typename T>
  torch::Tensor ToTensor(std::vector<T> vec, torch::TensorOptions options)
  {
    T array[vec.size()]; 
    for (int j(0); j < vec.size(); j++){array[j] = vec.at(j); }
    return torch::tensor(array, options); 
  }

  template<typename T>
  torch::Tensor ToTensor(std::vector<T> vec)
  {
    T array[vec.size()]; 
    for (int j(0); j < vec.size(); j++){array[j] = vec.at(j); }
    return torch::tensor(array); 
  }








};

#endif
