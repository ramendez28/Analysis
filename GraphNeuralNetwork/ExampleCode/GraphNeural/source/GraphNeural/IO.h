#ifndef IO_H
#define IO_H
#include<TFile.h>
#include<iostream>
#include<TString.h>

std::vector<std::map<TString, std::multimap<int, std::map<TString, float>>>> ReadRootFile(TFile* file); 

#endif
