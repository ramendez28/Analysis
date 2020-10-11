#include <TChain.h>
#include <vector>
#include <TTreeReader.h>
#include <TChain.h>

TH2F* Graphing(TH2F* Graph, TChain *Chain, float Luminosity)
{
  TTreeReader Reader(Chain);
  TTreeReaderValue<float> MET(Reader, "met");
  TTreeReaderValue<unsigned int> nJets(Reader, "njets");
  TTreeReaderValue<float> Weighting(Reader, "weight_nominal");
  while (Reader.Next())
  {
    Graph -> Fill(*nJets, *MET, *Weighting * Luminosity);
  }
  return Graph;
}


void AIDA_TChain()
{
  // Defining the used directories for data and monte carlo
  string Data_Dir = "/home/tnom6927/Dokumente/Doctor of Philosophy (PhD) University of Sydney/Project/Data/Samples_by_Carl";
  string Monte_Carlo_Dir = Data_Dir + "/MonteCarlo/";
  string Measurement_Data_Dir = Data_Dir + "/MeasurementData/";

  // Initiating the TChain for the WtLoop_nominal tree
  auto Data = new TChain("WtLoop_nominal");
  auto MonteCarlo = new TChain("WtLoop_nominal");

  // Here we define the names of the root files in a vector
  vector<string> Data_Names = {"Data15_data15_Data_Data_nominal.root", "Data16_data16_Data_Data_nominal.root", "Data17_data17_Data_Data_nominal.root"};
  vector<string> MonteCarloA_Names = {"ttbar_410472_FS_MC16a_nominal.root", "tW_DR_410648_FS_MC16a_nominal.root", "tW_DR_410649_FS_MC16a_nominal.root"};
  vector<string> MonteCarloD_Names = {"ttbar_410472_FS_MC16d_nominal.root", "tW_DR_410648_FS_MC16d_nominal.root", "tW_DR_410649_FS_MC16d_nominal.root"};

  // Populating the TChain
  for (auto& Name : Data_Names) {Data -> Add((Measurement_Data_Dir + Name).c_str());}
  for (auto& Name : MonteCarloA_Names) {MonteCarlo -> Add((Monte_Carlo_Dir + Name).c_str());}
  for (auto& Name : MonteCarloD_Names) {MonteCarlo -> Add((Monte_Carlo_Dir + Name).c_str());}

  // weight_nominal, njets, met, mass_lep1lep2
  float Max_MET = Data -> GetMaximum("met");
  float Max_Njets = Data -> GetMaximum("njets");
  float Lumi = 13.4 + 25.1 + 37.8; // 2015, 2016 and 2017
  int Number_Of_Bins = 20;
  int bin_x = 6;

  auto Canv = new TCanvas("Canvas", "Canvas", 1600, 800);
  auto Histogram_Data = new TH2F("Histogram_Data", "N_jets vs Missing ET;N Jets;Missing ET (GeV)",
                              bin_x, 0, 6, Number_Of_Bins, 0, 400);
  Histogram_Data = Graphing(Histogram_Data, Data, Lumi);

  auto Histogram_MC = new TH2F("Histogram_MC", "N_Jets vs Missing ET;N Jets;Missing ET (GeV)",
                              bin_x, 0, 6, Number_Of_Bins, 0, 400);
  Histogram_MC = Graphing(Histogram_MC, MonteCarlo, Lumi);

  Canv -> Divide(2);
  Canv -> cd(1); Histogram_Data -> Draw("Lego2");
  Canv -> cd(2); Histogram_MC -> Draw("Lego1");
}
