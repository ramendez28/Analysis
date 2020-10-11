#include <vector>
#include <TFile.h>
#include <TTreeReader.h>
#include <TSystem.h>

using namespace std;

// function which returns the root entries given dir, Tree name and Branch
template<class T> vector<T>* Read_ROOT(string directory, string Tree, string Branch)
{
  // Opening the root file
  TFile root_file(directory.c_str());

  // Reading the Tree
  TTreeReader Data_Set(Tree.c_str(), &root_file);
  TTreeReaderValue<T> NTuple(Data_Set, Branch.c_str());

  // Creating a vector (array to be returned )
  auto Data = new vector <T>;

  // Returning the individual entries
  while (Data_Set.Next())
  {
    Data->push_back(*NTuple);
  }

  return Data;
}

void AIDA_Read_Data(){

  // Filenames
  string File_Names[] = {"MonteCarlo/ttbar_410472_FS_MC16a_nominal.root", "MonteCarlo/ttbar_410472_FS_MC16d_nominal.root", "MonteCarlo/tW_DR_410648_FS_MC16a_nominal.root","MonteCarlo/tW_DR_410648_FS_MC16d_nominal.root", "MonteCarlo/tW_DR_410649_FS_MC16a_nominal.root","MonteCarlo/tW_DR_410649_FS_MC16d_nominal.root"};

  // Data Files
  string Data_Filenames[] = {"MeasurementData/Data15_data15_Data_Data_nominal.root", "MeasurementData/Data16_data16_Data_Data_nominal.root", "MeasurementData/Data17_data17_Data_Data_nominal.root"};

  // specifying the root directory as string
  string Data_Directory = "/home/tnom6927/Dokumente/Doctor of Philosophy (PhD) University of Sydney/Project/Data/Samples_by_Carl/";

  // Loop through each filename
  string Directory;

  // Creating multiple vectors
  vector<float> All_N_Jets;
  vector<float> All_Weights;
  vector<float> All_Missing_ET;

  for (const string &text : File_Names)
  {

    // Append the filenames with the directory
    Directory = Data_Directory + text;

    // Check if the file is in the current directory
    if (gSystem -> AccessPathName(Directory.c_str()) == false)
    {
      // Print the current file being accessed
      cout << "Processing current ROOT file: " << Directory << endl;

      // Reading the ROOT files and getting Monte Carlo data
      auto Weight_Normal = Read_ROOT<float>(Directory, "WtLoop_nominal", "weight_nominal");
      auto N_jets = Read_ROOT<unsigned int>(Directory, "WtLoop_nominal", "njets");
      auto Missing_ET = Read_ROOT<float>(Directory, "WtLoop_nominal", "met");
      cout << "Size of the Jet sample: " << N_jets -> size() << endl;
      cout << "Size of the Weight Normal: " << Weight_Normal ->size() << endl;
      cout << "Size of the Missing ET sample: " << Missing_ET -> size() << endl;

      for (unsigned i = 0; i < Missing_ET -> size(); i++)
      {
        // Reading entries and storing them
        All_N_Jets.push_back(N_jets -> at(i));
        All_Weights.push_back(Weight_Normal -> at(i));
        All_Missing_ET.push_back(Missing_ET -> at(i));
      }

      // Garbage
      N_jets -> clear();
      Weight_Normal -> clear();
      Missing_ET -> clear();
    }
  }

  // Find the max and the min values of the data points
  auto Max_jets = *max_element(All_N_Jets.begin(), All_N_Jets.end());
  auto Min_jets = *min_element(All_N_Jets.begin(), All_N_Jets.end());
  auto Max_MET = *max_element(All_Missing_ET.begin(), All_Missing_ET.end());
  auto Min_MET = *min_element(All_Missing_ET.begin(), All_Missing_ET.end());


  cout << "__________________________Monte Carlo DATA______________________________________" << endl;
  cout << "Max Jets found: " << Max_jets << " Min Jets found: " << Min_jets << " \n"
       << "Max Missing ET: " << Max_MET << " Min Missing ET: " << Min_MET << "\n";
  cout << "_________________________________________________________________________________" << endl;

  vector<float> All_N_Jets_Data;
  vector<float> All_Weights_Data;
  vector<float> All_Missing_ET_Data;

  for (const string &text : Data_Filenames)
  {
    Directory = Data_Directory + text;
    auto Weight_Normal_Data = Read_ROOT<float>(Directory, "WtLoop_nominal", "weight_nominal");
    auto N_jets_Data = Read_ROOT<unsigned int>(Directory, "WtLoop_nominal", "njets");
    auto Missing_ET_Data = Read_ROOT<float>(Directory, "WtLoop_nominal", "met");
    cout << "________" << text << "________" << endl;
    cout << "Size of the Jet sample: " << N_jets_Data -> size() << endl;
    cout << "Size of the Weight Normal: " << Weight_Normal_Data ->size() << endl;
    cout << "Size of the Missing ET sample: " << Missing_ET_Data -> size() << endl;
    for (unsigned i = 0; i < Missing_ET_Data -> size(); i++)
    {
      All_N_Jets_Data.push_back(N_jets_Data -> at(i));
      All_Weights_Data.push_back(Weight_Normal_Data -> at(i));
      All_Missing_ET_Data.push_back(Missing_ET_Data -> at(i));
    }
    Weight_Normal_Data -> clear();
    N_jets_Data -> clear();
    Missing_ET_Data -> clear();
  }

  // Simple Histogram formating and generation
  gStyle -> SetPalette(kBird);
  gStyle -> SetOptStat(0);
  gStyle -> SetOptTitle(0);

  int Number_Of_Bins = 150;
  Max_jets = 10.;
  Max_MET = 600.;

  // Monte Carlo Histogram
  auto Histogram_MC = new TH2F("Histogram_MC", "N_jets vs Missing;N jets;Missing ET (GeV)",
                              Max_jets, 0, Max_jets, Number_Of_Bins, 0, Max_MET);

  float Lumi = 13.4 + 25.1 + 37.8; // 2015, 2016 and 2017
  for (unsigned i = 0; i < All_Missing_ET.size(); i++)
  {
    Histogram_MC -> Fill(All_N_Jets[i], All_Missing_ET[i], Lumi * All_Weights[i]);
  }

  // Data Histogram
  auto Histogram_Data = new TH2F("Histogram_MC", "N_jets vs Missing;N jets;Missing ET (GeV)",
                              Max_jets, 0, Max_jets, Number_Of_Bins, 0, Max_MET);

  for (unsigned i = 0; i < All_Missing_ET_Data.size(); i++)
  {
    Histogram_Data -> Fill(All_N_Jets_Data[i], All_Missing_ET_Data[i], All_Weights_Data[i]);
  }

  All_N_Jets.clear();
  All_Missing_ET.clear();
  All_Weights.clear();
  All_N_Jets_Data.clear();
  All_Missing_ET_Data.clear();
  All_Weights_Data.clear();

  // Generating a TCanvas
  auto c = new TCanvas("Canvas", "Canvas", 1600, 800);
  c -> Divide(3);
  c -> cd(1); Histogram_MC -> Draw("Lego2");
  c -> cd(2); Histogram_Data -> Draw("Lego1");

  auto Histogram_MC_Clone = Histogram_MC -> Clone();
  Histogram_MC -> Divide(Histogram_Data);

  c -> cd(3); Histogram_MC_Clone -> Draw("Lego2");
}

int main()
{
  AIDA_Read_Data();
  return 0;
}
