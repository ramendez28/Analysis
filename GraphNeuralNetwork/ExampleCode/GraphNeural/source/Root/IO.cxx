#include<IO.h>
#include<TTree.h>
#include<TLeaf.h>
#include<Particle_Functions.h>

std::vector<std::map<TString, std::multimap<int, std::map<TString, float>>>> ReadRootFile(TFile* file) 
{
  TTree *t1 = (TTree*)file -> Get("LHEF");
  std::vector<std::map<TString, std::multimap<int, std::map<TString, float>>>> Output; 
  
  for (int i(0); i < t1 -> GetEntries(); i++)
  {
    t1 -> GetEntry(i, 1); 
    int E = t1 -> GetLeaf("Event.Number") -> GetValue(0); 
    int P_s = t1 -> GetLeaf("Particle_size") -> GetValue(0);  

    std::map<TString, std::multimap<int, std::map<TString, float>>> Temp;   
    std::multimap<int, std::map<TString, float>> Decay_Chains; 
    std::multimap<int, std::map<TString, float>> MC_Final_State; 
    std::multimap<int, std::map<TString, float>> Initializer; 
    for (int x(0); x < P_s; x++)
    {
      float Mother1 = t1 -> GetLeaf("Particle.Mother1") -> GetValue(x); 
      float Mother2 = t1 -> GetLeaf("Particle.Mother2") -> GetValue(x); 

      std::map<TString, float> Attributes; 
      Attributes["Px"] = t1 -> GetLeaf("Particle.Px") -> GetValue(x); 
      Attributes["Py"] = t1 -> GetLeaf("Particle.Py") -> GetValue(x); 
      Attributes["Pz"] = t1 -> GetLeaf("Particle.Pz") -> GetValue(x); 
      Attributes["E"] = t1 -> GetLeaf("Particle.E") -> GetValue(x); 
      Attributes["M"] = t1 -> GetLeaf("Particle.M") -> GetValue(x); 
      Attributes["PID"] = t1 -> GetLeaf("Particle.PID") -> GetValue(x);  

      if (Mother1 == Mother2 && Mother1 > 0 && Mother2 > 0){Decay_Chains.insert(std::pair<int, std::map<TString, float>> (Mother1, Attributes));}
      if (Mother1 != Mother2){MC_Final_State.insert(std::pair<int, std::map<TString, float>> (Mother2, Attributes));}
      if (Mother1 == Mother2 && Mother1 < 0 && Mother2 < 0){Initializer.insert(std::pair<int, std::map<TString, float>> (Mother1, Attributes));}
    }
    Temp["Decay_Chains"] = Decay_Chains; 
    Temp["MC_Final_State"] = MC_Final_State; 
    Temp["Initial_State"] = Initializer; 
    Output.push_back(Temp);  
  }
  return Output;
}
