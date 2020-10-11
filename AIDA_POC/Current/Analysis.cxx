#include <TH1F.h>
#include <TFile.h>
#include <TRandom.h>
#include <TString.h>
#include <TChain.h>
#include <TSystem.h>
#include <iostream>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <unistd.h>

void CreateHistos(float Met, float Luminosity, bool Flavor, bool Charge, float Weight, TH1F* Histogram)
{
	std::string Name_Of_Hist = Histogram -> GetTitle();
	// This chooses events which are opposite charge and opposite flavor 
	if (Flavor == 1 && Charge == 1 && Name_Of_Hist.find("OFOC") != std::string::npos)
	{
		Histogram->Fill(Met, Luminosity*Weight); 		
	}
	// This chooses events with opposite flavor but same charge 
	else if (Flavor == 1 && Charge == 0 && Name_Of_Hist.find("OFSC") != std::string::npos)
	{
		Histogram->Fill(Met, Luminosity*Weight);
	}
	// This chooses events with same flavor but opposite charge 
	else if (Flavor == 0 && Charge == 1 && Name_Of_Hist.find("SFOC") != std::string::npos) 
	{
		Histogram->Fill(Met, Luminosity*Weight);
	}	
	// Same charge and same flavor
	else if (Flavor == 0 && Charge == 0 && Name_Of_Hist.find("SFSC") != std::string::npos)
	{
		Histogram->Fill(Met, Luminosity*Weight);
	}
}

void Histogram_Writer(string FileName, vector<TH1F*> Spawners, string Process)
{
	// Updating the root file with the histograms	
	TFile File (FileName.c_str(), "UPDATE");
	for (unsigned int x = 0; x < Spawners.size(); x++)
	{
		// Getting the next histogram pointer 
		TH1F* Histogram = Spawners[x];		
		
		if (Process == "Data")
		{
			for (unsigned int z = 0; z < 100; z++)
			{

				Histogram -> Fill(gRandom -> Poisson(100), gRandom -> Gaus(0.5,0.5));
			}
		}
		
		// Writing the histo to file 
		Histogram-> Write();	
	}
	File.Close();
}

void Clear_Vector(vector<TH1F*> Vector)
{
	for (auto p : Vector)
	{
		delete p;	
	}
}
void Analysis()
{
	// Defining the path to the Ntuples 
	const TString Path = "/home/tnom6927/POC_Fitting/Current/Example_With_Systematics/tW_Samples/"; //"/sydpp2/atlas/sgtop/ntuple4/";
	
	// Creating a string vector with the proceeses to be included in the Analysis
	vector<string> Processes = {"tW"};   //{"Diboson", "ttbar", "ttH", "ttV", "tW", "Wjets", "Zjets"};

	// Declaring a vector of type string for the file directory of the processes 
	vector<string> Directories;

	// Declaring the Chain_Sum
	vector<TChain*> Chaining;

	for (const auto &process : Processes)
	{
		// Initializing the chain at the start of the loop
		TChain *Chain = new TChain("Loop_nominal"); //new TChain("WtLoop_nominal");

		// Counting the number of files to be read for each process	
		int Files = 0;

		// Reading the files in the specified directory 
		void *Open_Dir = gSystem -> OpenDirectory(Path);
		
		// initiating the while loop
		while (auto Filename = static_cast<const Char_t*>(gSystem -> GetDirEntry(Open_Dir)))
		{
			// Changing the string type 
			string FileLocation { Filename };

			// Check substring inside the file 
			if (FileLocation.find(process) != std::string::npos)
			{
				Chain -> Add((string(Path) + Filename).c_str());
				Files =  Files + 1;	
			}
			
		}
		
		// Add the new chain to the chains 
		Chaining.emplace_back(Chain);

		std::cout << "There are " << Files << " in " << process << std::endl;
	}
	
	std::cout << "##########################################################" << std::endl;

	// Some parameters for the histograms 
	float Energy_Limit = 250; // Units are in GeV
	Double_t Max_Energy = Energy_Limit;
	int Bins = 20;
	float Luminosity = 3.21956 + 32.9881; //140.5; // Total measured luminosity
	
	// Defining the titles for the histograms according to the different parameters of interest
	vector<string> Titles = {"O-Flav, O-Char", "O-Flav, S-Char", "S-Flav, O-Char", "S-Flav, S-Char"};
	const vector<string> Names = {"OFOC","OFSC", "SFOC", "SFSC"};

	// Generating the Histograms for each Standard Model Process as a vector
	vector<TH1F*> Data_Jets;
	vector<TH1F*> Data_NoJ;

	
	// Creating a new root file to write the histograms to 	
	for (unsigned int i = 0; i < Chaining.size(); i++)
	{
		
		// Importing the trees to the reader
		string Process = Processes.at(i);
		std::cout << "Opening: " << Process << std::endl;
		TTreeReader Reader(Chaining[i]);
	
		for (unsigned int N_T = 0; N_T < Titles.size(); N_T++)
		{
			TH1F* Jet = new TH1F((Titles.at(N_T) + "Data").c_str(), (Names.at(N_T) + "Data").c_str(), Bins, 0, Max_Energy);
			TH1F* No_Jet = new TH1F((Titles.at(N_T) + "Data").c_str(), (Names.at(N_T) + "Data").c_str(), Bins, 0, Max_Energy);	
			Data_Jets.emplace_back(Jet);	
			Data_NoJ.emplace_back(No_Jet);
		}
			
		// Defining the branches to extract from the trees 
		TTreeReaderValue<float> MET(Reader, "met");
		TTreeReaderValue<float> Nominal(Reader, "weight_nominal");
		TTreeReaderValue<bool> Opposite_Signed(Reader, "OS");
		TTreeReaderValue<bool> Opposite_Flavor(Reader, "elmu");
		TTreeReaderValue<unsigned int> N_Jets(Reader, "njets");

		// Adding the systematic varibles to the data sets
		TTreeReaderValue<float> muR_Down(Reader, "weight_sys_scale_muR_05");
		TTreeReaderValue<float> muR_Up(Reader, "weight_sys_scale_muR_20");

		TTreeReaderValue<float> muF_Down(Reader, "weight_sys_scale_muF_05");
		TTreeReaderValue<float> muF_Up(Reader, "weight_sys_scale_muF_20");

		TTreeReaderValue<float> ISR_Down(Reader, "weight_sys_isr_alphaS_Var3cDown");
		TTreeReaderValue<float> ISR_Up(Reader, "weight_sys_isr_alphaS_Var3cUp");

		TTreeReaderValue<float> JVT_Down(Reader, "weight_sys_jvt_DOWN");
		TTreeReaderValue<float> JVT_Up(Reader, "weight_sys_jvt_UP");
		
		TTreeReaderValue<float> EL_ScaleFactor_ID_Down(Reader, "weight_sys_leptonSF_EL_SF_ID_DOWN");
		TTreeReaderValue<float> EL_ScaleFactor_ID_Up(Reader, "weight_sys_leptonSF_EL_SF_ID_UP");
	
		TTreeReaderValue<float> EL_ScaleFactor_Isol_Down(Reader, "weight_sys_leptonSF_EL_SF_Isol_DOWN");
		TTreeReaderValue<float> EL_ScaleFactor_Isol_Up(Reader, "weight_sys_leptonSF_EL_SF_Isol_UP");
	
		TTreeReaderValue<float> EL_ScaleFactor_Reco_Down(Reader, "weight_sys_leptonSF_EL_SF_Reco_DOWN");
		TTreeReaderValue<float> EL_ScaleFactor_Reco_Up(Reader, "weight_sys_leptonSF_EL_SF_Reco_UP");

		TTreeReaderValue<float> EL_ScaleFactor_Trigger_Down(Reader, "weight_sys_leptonSF_EL_SF_Trigger_DOWN");
		TTreeReaderValue<float> EL_ScaleFactor_Trigger_Up(Reader, "weight_sys_leptonSF_EL_SF_Trigger_UP");

		TTreeReaderValue<float> MU_ScaleFactor_ID_Stat_Down(Reader, "weight_sys_leptonSF_MU_SF_ID_STAT_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_ID_Stat_Up(Reader, "weight_sys_leptonSF_MU_SF_ID_STAT_UP");

		TTreeReaderValue<float> MU_ScaleFactor_ID_Stat_LowPT_Down(Reader, "weight_sys_leptonSF_MU_SF_ID_STAT_LOWPT_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_ID_Stat_LowPT_Up(Reader, "weight_sys_leptonSF_MU_SF_ID_STAT_LOWPT_UP");

		TTreeReaderValue<float> MU_ScaleFactor_ID_Syst_Down(Reader, "weight_sys_leptonSF_MU_SF_ID_SYST_DOWN");	
		TTreeReaderValue<float> MU_ScaleFactor_ID_Syst_Up(Reader, "weight_sys_leptonSF_MU_SF_ID_SYST_UP");

		TTreeReaderValue<float> MU_ScaleFactor_ID_Syst_LowPT_Down(Reader, "weight_sys_leptonSF_MU_SF_ID_SYST_LOWPT_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_ID_Syst_LowPT_Up(Reader, "weight_sys_leptonSF_MU_SF_ID_SYST_LOWPT_UP");
		
		TTreeReaderValue<float> MU_ScaleFactor_Isol_Stat_Down(Reader, "weight_sys_leptonSF_MU_SF_Isol_STAT_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_Isol_Stat_Up(Reader, "weight_sys_leptonSF_MU_SF_Isol_STAT_UP");
	
		TTreeReaderValue<float> MU_ScaleFactor_Isol_Syst_Down(Reader, "weight_sys_leptonSF_MU_SF_Isol_SYST_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_Isol_Syst_Up(Reader, "weight_sys_leptonSF_MU_SF_Isol_SYST_UP");

		TTreeReaderValue<float> MU_ScaleFactor_Trigger_Stat_Down(Reader, "weight_sys_leptonSF_MU_SF_Trigger_STAT_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_Trigger_Stat_Up(Reader, "weight_sys_leptonSF_MU_SF_Trigger_STAT_UP");

		TTreeReaderValue<float> MU_ScaleFactor_Trigger_Syst_Down(Reader, "weight_sys_leptonSF_MU_SF_Trigger_SYST_DOWN");
		TTreeReaderValue<float> MU_ScaleFactor_Trigger_Syst_Up(Reader, "weight_sys_leptonSF_MU_SF_Trigger_SYST_UP");

		TTreeReaderValue<float> PileUp_Down(Reader, "weight_sys_pileup_DOWN");
		TTreeReaderValue<float> PileUp_Up(Reader, "weight_sys_pileup_UP");

		// Generating the Histograms for the SM processes and the Systematics 
		vector<TH1F*> Histograms_Jets;
		vector<TH1F*> Histograms_NoJets;	
		vector<TH1F*> Systematics_Down_Jets;
		vector<TH1F*> Systematics_Up_Jets;
		vector<TH1F*> Systematics_Down_NoJets;
		vector<TH1F*> Systematics_Up_NoJets;
						
		// A name variable used for the different name for loops 
		for (unsigned int N_T = 0; N_T < Titles.size(); N_T++)               		
		{
			TH1F* Hist_Jet = new TH1F((Titles.at(N_T) + "_" +  Process).c_str(), (Names.at(N_T) + "_" + Process).c_str(), Bins, 0, Max_Energy);
			Histograms_Jets.emplace_back(Hist_Jet);

			TH1F* Hist_NoJet = new TH1F((Titles.at(N_T)+"NoJet" + "_" + Process).c_str(), (Names.at(N_T) + "_" + Process).c_str(), Bins, 0, Max_Energy);		
			Histograms_NoJets.emplace_back(Hist_NoJet);
		}
		 
     		vector<std::string> Systematic_Titles = {"muR", "muF", "ISR", "JVT", "EL_ScaleFactor_ID", "EL_ScaleFactor_Isol", "EL_ScaleFactor_Reco", "EL_ScaleFactor_Trigger", "MU_ScaleFactor_ID_Stat", "MU_ScaleFactor_ID_Stat_LowPT", "MU_ScaleFactor_ID_Syst", "MU_ScaleFactor_ID_Syst_LowPT", "MU_ScaleFactor_Isol_Stat", "MU_ScaleFactor_Isol_Syst", "MU_ScaleFactor_Trigger_Stat", "MU_ScaleFactor_Trigger_Syst", "PileUp"};

		// Systematics TH1Fs being generated for every process and all the different selections 
		for (std::string Selection : Names)
		{
			for (std::string System: Systematic_Titles)
			{
				TH1F* Histo_Down = new TH1F((Selection + "_" + System + "_Down" + "_" + Process).c_str(), (Selection  + "_" + System  + "_Down" + "_" + Process).c_str(), Bins, 0 , Max_Energy);
				Systematics_Down_Jets.emplace_back(Histo_Down);
				Systematics_Down_NoJets.emplace_back(Histo_Down);

				TH1F* Histo_Up = new TH1F((Selection + "_" + System  + "_Up" + "_" + Process).c_str(), (Selection + "_" + System  + "_Up" + "_" + Process).c_str(), Bins, 0 , Max_Energy);
				Systematics_Up_Jets.emplace_back(Histo_Up);
				Systematics_Up_NoJets.emplace_back(Histo_Up);
			}
		}

		while (Reader.Next())
		{
			
			// Defining the discriminating variables 	
			bool Flavor = *Opposite_Flavor;
			bool Opposite_Charge = *Opposite_Signed;
			int Jets = *N_Jets;
			float Missing_ET = *MET;

			// Systematics Up
			float S_muR_Up = *muR_Up;
			float S_muF_Up = *muF_Up;
			float S_ISR_Up = *ISR_Up;
			float S_JVT_Up = *JVT_Up;
			float S_EL_ScaleFactor_ID_Up = *EL_ScaleFactor_ID_Up;
			float S_EL_ScaleFactor_Isol_Up = *EL_ScaleFactor_Isol_Up;
			float S_EL_ScaleFactor_Reco_Up = *EL_ScaleFactor_Reco_Up;
			float S_MU_ScaleFactor_ID_Stat_LowPT_Up = *MU_ScaleFactor_ID_Stat_LowPT_Up;
			float S_MU_ScaleFactor_ID_Syst_Up = *MU_ScaleFactor_ID_Syst_Up;
			float S_MU_ScaleFactor_ID_Syst_LowPT_Up = *MU_ScaleFactor_ID_Syst_LowPT_Up;
			float S_MU_ScaleFactor_Isol_Stat_Up = *MU_ScaleFactor_Isol_Stat_Up;
			float S_MU_ScaleFactor_Isol_Syst_Up = *MU_ScaleFactor_Isol_Syst_Up;
			float S_MU_ScaleFactor_Trigger_Stat_Up = *MU_ScaleFactor_Trigger_Stat_Up;
			float S_MU_ScaleFactor_Trigger_Syst_Up = *MU_ScaleFactor_Trigger_Syst_Up;
			float S_MU_ScaleFactor_ID_Stat_Up = *MU_ScaleFactor_ID_Stat_Up;
			float S_EL_ScaleFactor_Trigger_Up = *EL_ScaleFactor_Trigger_Up; 
			float S_PileUp_Up = *PileUp_Up;
					 
			// Systematics Down
			float S_muR_Down = *muR_Down;
			float S_muF_Down = *muF_Down;
			float S_ISR_Down = *ISR_Down;
			float S_JVT_Down = *JVT_Down;
			float S_EL_ScaleFactor_ID_Down = *EL_ScaleFactor_ID_Down;
			float S_EL_ScaleFactor_Isol_Down = *EL_ScaleFactor_Isol_Down;
			float S_EL_ScaleFactor_Reco_Down = *EL_ScaleFactor_Reco_Down;
			float S_EL_ScaleFactor_Trigger_Down = *EL_ScaleFactor_Trigger_Down;
			float S_MU_ScaleFactor_ID_Stat_LowPT_Down = *MU_ScaleFactor_ID_Stat_LowPT_Down;
			float S_MU_ScaleFactor_ID_Syst_LowPT_Down = *MU_ScaleFactor_ID_Syst_LowPT_Down;
			float S_MU_ScaleFactor_ID_Syst_Down = *MU_ScaleFactor_ID_Syst_Down;
			float S_MU_ScaleFactor_Isol_Stat_Down = *MU_ScaleFactor_Isol_Stat_Down;
			float S_MU_ScaleFactor_Isol_Syst_Down = *MU_ScaleFactor_Isol_Syst_Down;
			float S_MU_ScaleFactor_Trigger_Stat_Down = *MU_ScaleFactor_Trigger_Stat_Down;
			float S_MU_ScaleFactor_Trigger_Syst_Down = *MU_ScaleFactor_Trigger_Syst_Down;
			float S_MU_ScaleFactor_ID_Stat_Down = *MU_ScaleFactor_ID_Stat_Down;
			float S_PileUp_Down = *PileUp_Down;

			// Adding the overflow events to the last bin in the histograms 
			if (Missing_ET >= Energy_Limit)
			{
				Missing_ET = Energy_Limit-1;
			}
			if (Jets != 0)
			{
				for (unsigned int index = 0; index < Histograms_Jets.size(); index++)
				{
					CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, *Nominal, Histograms_Jets[index]);
					CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, *Nominal, Data_Jets[index]);
				}

				for (unsigned int index = 0; index < Systematics_Down_Jets.size(); index++)
				{
					std::string Down = Systematics_Down_Jets[index] -> GetTitle();
					std::string Up = Systematics_Up_Jets[index] -> GetTitle();

					if (Down.find("muR") != std::string::npos && Up.find("muR") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_muR_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_muR_Up, Systematics_Up_Jets[index]);
					}
					else if (Down.find("muF") != std::string::npos && Up.find("muF") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_muF_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_muF_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("ISR") != std::string::npos && Up.find("ISR") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_ISR_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_ISR_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("JVT") != std::string::npos && Up.find("JVT") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_JVT_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_JVT_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("EL_ScaleFactor_ID") != std::string::npos && Up.find("EL_ScaleFactor_ID") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_ID_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_ID_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("EL_ScaleFactor_Isol") != std::string::npos && Up.find("EL_ScaleFactor_Isol") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_Isol_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_Isol_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("EL_ScaleFactor_Reco") != std::string::npos && Up.find("EL_ScaleFactor_Reco") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_Reco_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_Reco_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_ID_Stat_LowPT") != std::string::npos && Up.find("MU_ScaleFactor_ID_Stat_LowPT") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Stat_LowPT_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Stat_LowPT_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_ID_Syst") != std::string::npos && Up.find("MU_ScaleFactor_ID_Syst") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Syst_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Syst_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_ID_Stat") != std::string::npos && Up.find("MU_ScaleFactor_ID_Stat") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Stat_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Stat_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_ID_Syst_LowPT") != std::string::npos && Up.find("MU_ScaleFactor_ID_Syst_LowPT") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Syst_LowPT_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_ID_Syst_LowPT_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_Isol_Stat") != std::string::npos && Up.find("MU_ScaleFactor_Isol_Stat") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Isol_Stat_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Isol_Stat_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_Isol_Syst") != std::string::npos && Up.find("MU_ScaleFactor_Isol_Syst") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Isol_Syst_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Isol_Syst_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_Trigger_Stat") != std::string::npos && Up.find("MU_ScaleFactor_Trigger_Stat") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Trigger_Stat_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Trigger_Stat_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("MU_ScaleFactor_Trigger_Syst") != std::string::npos && Up.find("MU_ScaleFactor_Trigger_Syst") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Trigger_Syst_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_MU_ScaleFactor_Trigger_Syst_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("EL_ScaleFactor_Trigger") != std::string::npos && Up.find("EL_ScaleFactor_Trigger") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_Trigger_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_EL_ScaleFactor_Trigger_Up, Systematics_Up_Jets[index]);					
					}
					else if (Down.find("PileUp") != std::string::npos && Up.find("PileUp") != std::string::npos)
					{
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_PileUp_Down, Systematics_Down_Jets[index]);
						CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, S_PileUp_Up, Systematics_Up_Jets[index]);					
					}
				}
				
			}
			else 
			{
				//CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, Weight, Process_Spawn_Jets); 
				//CreateHistos(Missing_ET, Luminosity, Flavor, Opposite_Charge, Weight, Data_Jets);
			}
		
		}

		for (unsigned int id = 0; id < Systematics_Up_Jets.size(); id++)
		{
			auto Temp = Systematics_Up_Jets[id];
			auto Temp2 = Systematics_Down_Jets[id];
			Histograms_Jets.emplace_back(Temp);
			Histograms_Jets.emplace_back(Temp2);
		}
		// Writing the jet histograms
		Histogram_Writer("Histograms_Jets.root", Histograms_Jets, Process);



		// Clearning out the pointers in the vectors 
		Clear_Vector(Histograms_Jets);

		//Clear_Vector(Histograms_NoJets);	
		//Clear_Vector(Systematics_Up_Jets);
		//Clear_Vector(Systematics_Down_Jets);
		//Clear_Vector(Systematics_Up_NoJets);
		//Clear_Vector(Systematics_Down_NoJets);

		// Writing the jet histograms 
		//Histogram_Writer("Histograms_Jets.root", Process_Spawn_Jets, "None");
		
	}	
	Histogram_Writer("Histograms_Jets.root", Data_Jets, "Data");
	//Histogram_Writer("Histogram_Data_Jets.root", Data_Jets, "Data", Names);
}
