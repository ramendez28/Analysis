#ifndef PARTICLE_FUNCTIONS_H
#define PARTICLE_FUNCTIONS_H
#include<TString.h>
#include<map>
#include<iostream>


TString PDG_To_String(unsigned int pdg);
float Invariant_Mass(int px, int py, int pz, int E); 
void VerifyProcess(std::vector<std::map<TString, std::multimap<int, std::map<TString, float>>>> Data, int index = 0);


#endif
