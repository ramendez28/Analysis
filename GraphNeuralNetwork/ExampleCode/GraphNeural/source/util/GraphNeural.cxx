#include<iostream>
#include<IO.h>
#include<Particle_Functions.h>
#include<UnitTests.h>

int main()
{
 
  //TFile* F = new TFile("../data/W_to_lepton.root"); 
  //std::vector<std::map<TString, std::multimap<int, std::map<TString, float>>>> Data = ReadRootFile(F); 
  
  //for (int i(0); i < 10; i++)
  //{
  //  VerifyProcess(Data, i);   
  //} 

  TensorTests::TestTensorConversion();   
  //TestGeometricData::TestCreateObject(); 


  return 0; 

}
