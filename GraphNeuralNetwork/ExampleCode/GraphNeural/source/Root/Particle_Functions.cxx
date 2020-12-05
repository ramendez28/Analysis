#include<Particle_Functions.h>

TString PDG_To_String(unsigned int pdg)
{
  std::map<int, TString> PDG_map; 
  
  //====== Quarks 
  PDG_map[1] = "d"; 
  PDG_map[-1] = "d~"; 
  PDG_map[2] = "u"; 
  PDG_map[-2] = "u~"; 
  PDG_map[3] = "s"; 
  PDG_map[-3] = "s~"; 
  PDG_map[4] = "c"; 
  PDG_map[-4] = "c~"; 
  PDG_map[5] = "b"; 
  PDG_map[-5] = "b~"; 
  PDG_map[6] = "t"; 
  PDG_map[-6] = "t~"; 

  // ======= Leptons 
  // electron 
  PDG_map[11] = "e-"; 
  PDG_map[-11] = "e+"; 
  PDG_map[12] = "ve"; 
  PDG_map[-12] = "ve~";
 
  // Muon 
  PDG_map[13] = "mu-"; 
  PDG_map[-13] = "mu+"; 
  PDG_map[14] = "vmu"; 
  PDG_map[-14] = "vmu~";

  // ======= Boson 
  // Boson 
  PDG_map[24] = "W+"; 
  PDG_map[-24] = "W-"; 
  PDG_map[23] = "Z0"; 
  PDG_map[21] = "g";

  return PDG_map[pdg];
}

float Invariant_Mass(int px, int py, int pz, int E)
{
  float p2 = std::pow(E, 2) - (std::pow(px, 2) + std::pow(py, 2) + std::pow(pz, 2)); 
  return std::sqrt(p2); 
}

void VerifyProcess(std::vector<std::map<TString, std::multimap<int, std::map<TString, float>>>> Data, int index)
{
  std::map<TString, std::multimap<int, std::map<TString, float>>> Test = Data[index];
 
  std::multimap<int, std::map<TString, float>> Initial_State = Test["Initial_State"]; 
  std::multimap<int, std::map<TString, float>> MC_State = Test["MC_Final_State"]; 
  std::multimap<int, std::map<TString, float>> Decays = Test["Decay_Chains"]; 

  typedef std::multimap<int, std::map<TString, float>>::iterator M; 
  
  TString total = "";
  for (M it = Initial_State.begin(); it != Initial_State.end(); it++)
  {
    std::map<TString, float> initial = it -> second; 
    total += PDG_To_String(initial["PID"]);  
    total += " "; 
  }

  total += "-> "; 

  for (M it = MC_State.begin(); it != MC_State.end(); it++)
  {
    std::map<TString, float> initial = it -> second; 
    total += PDG_To_String(initial["PID"]);  
    total += " ";  
  }

  total += "-> "; 

  for (M it = Decays.begin(); it != Decays.end(); it++)
  {
    std::map<TString, float> initial = it -> second; 
    total += PDG_To_String(initial["PID"]);  
    total += " "; 
  }

  std::cout << total << std::endl; 

}





























