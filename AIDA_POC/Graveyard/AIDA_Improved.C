#include <TChain.h>
#include <iostream>
#include <vector>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TH2F.h>
#include <TCanvas.h>
#include <TApplication.h>

using namespace std;

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

void AIDA_Improved()
{
  // Defining the main directory for data and Monte Carlo
  string ROOT_Dir = "/home/tnom6927/Dokumente/Doctor of Philosophy (PhD) University of Sydney/Project/Data/Samples_by_Carl";
  string Data = ROOT_Dir + "/MeasurementData/*";
  string MonteCarloA = ROOT_Dir + "/MonteCarlo/A/*";
  string MonteCarloD = ROOT_Dir + "/MonteCarlo/D/*";
  string MonteCarloE = ROOT_Dir + "/MonteCarlo/E/*";
  float Luminosity = 13.4 + 25.1 + 37.8; // 2015, 2016 and 2017

  // Initiating the TChain for the WtLoop_nominal Tree
  auto Data_Samples = new TChain("WtLoop_nominal");
  auto MonteCarlo = new TChain("WtLoop_nominal");
  Data_Samples -> Add(Data.c_str());
  MonteCarlo -> Add(MonteCarloA.c_str());
  MonteCarlo -> Add(MonteCarloD.c_str());
  MonteCarlo -> Add(MonteCarloE.c_str());

  int Number_Of_Bins = 20;
  int bin_x = 6;
  float Data_Max = Data_Samples -> GetMaximum("met");
  float MC_Max = MonteCarlo -> GetMaximum("met");

  auto Canv = new TCanvas("Canvas", "Canvas", 1600, 800);
  auto Histogram_Data = new TH2F("Histogram Data", "Number of jets vs Missing ET;Number of Jets;Missing ET (GeV)",
                            bin_x, 0 , 6, Number_Of_Bins, 0, 600);
  auto Histogram_MC = new TH2F("Histogram Monte Carlo", "Number of jets vs Missing ET;Number of Jets;Missing ET (GeV)",
                            bin_x, 0 , 6, Number_Of_Bins, 0, 600);

  Histogram_Data = Graphing(Histogram_Data, Data_Samples, Luminosity);
  Histogram_MC = Graphing(Histogram_MC, MonteCarlo, Luminosity);

  Canv -> Divide(2);
  Canv -> cd(1); Histogram_Data -> Draw("Lego2");
  Canv -> cd(2); Histogram_MC -> Draw("Lego1");
}
void StandaloneApplications(int argc, char** argv)
{
  AIDA_Improved();
}

int main(int argc, char** argv)
{
  TApplication app("ROOT Application", &argc, argv);
  StandaloneApplications(app.Argc(), app.Argv());
  app.Run();
  return 0;
}
