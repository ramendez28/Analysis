#include <TTreeReader.h>
#include <TTreeReaderValue.h>

void Files(TString root_dir, string SM_Process, vector<string> *Output_List)
{
	// Here we invoke the ROOT class that will open the directory.
	void *Open_Dir = gSystem -> OpenDirectory(root_dir);

	// Defining required variable that need to be passed to GetPathInfo.
	Char_t *Filename;
	Long_t id, size, flags, modtime;
	
	// Usign GetDirEntry to loop over the directory files including any dir.
	while ((Filename = (Char_t*) gSystem -> GetDirEntry(Open_Dir)))
	{
		// Concatinating the directory with the file 
		TString filepath = Form("%s/%s", root_dir.Data(), Filename);

		// Picking up file information using the previously defined variables 
		gSystem -> GetPathInfo(filepath.Data(), &id, &size, &flags, &modtime);

		// Check if the entry is a sub directory or a file 
		Int_t isDir = (02 & flags);
		string Type = isDir ? "Directory" : "File";

		// String compare. 
		if (Type == "File")
		{
			if (!string(Filename).find(SM_Process))
			{
				Output_List -> push_back(string(filepath));
			}
		}
	}		
}
 
void Graphing(vector<TH1F*> *Histogram_None, vector<TH1F*> *Histogram, const vector<string> *Files, string SM_Process)
{
	// The luminosity associated with the years 2015-2018
	float Luminosity = 140.5; // fb-1 
	float Max_MET = 250; // in GeV	

	TString name(SM_Process);
	if ( SM_Process == "Data")
	{
		Luminosity = 1;
	}

	// Generating the histograms 
	auto Jets_None = new TH1F((name+"None").Data(), (name).Data(), 20, 0, Max_MET);
	auto Jets_N = new TH1F((name).Data(), (name).Data(), 25, 0, Max_MET); 

	// Iterating through all the files and adding them to the TChain.
	TChain Chain("WtLoop_nominal");
	for (unsigned int i = 0; i < Files -> size(); i++)
	{
		cout << Files -> at(i) << endl;
		Chain.Add(Files->at(i).c_str());	
	}

	// Reading relevant variables from the TChain.
	TTreeReader Reader(&Chain);
	TTreeReaderValue<float> MET(Reader, "met");
	TTreeReaderValue<bool> E_U(Reader, "elmu");
	TTreeReaderValue<bool> OS(Reader, "OS");
	TTreeReaderValue<unsigned int> Jets(Reader, "njets");
	TTreeReaderValue<float> Weighting(Reader, "weight_nominal");
	
	while (Reader.Next())
	{
		// Dereferencing the pointers
		bool Flavor = *E_U;
		int N_Jets = *Jets;
		float Missing_ET = *MET;
		int Opposite_Charge = *OS;
	
		// operator that triggers only if electron and muon have opposite charge.
		//if (Flavor == 1 &&  Opposite_Charge == 1)
		if (Flavor == 1)
		{
			// This block add to the overflowing MET 
			if ( Missing_ET >= Max_MET)
			{
				Missing_ET = Max_MET-1;
			}

			// Filters for more than 0 jets.
			if (N_Jets == 0)
			{
				Jets_None -> Fill(Missing_ET , *Weighting*Luminosity);
			}
			if (N_Jets >=1)
			{
				Jets_N -> Fill(Missing_ET, *Weighting*Luminosity);
			}

		}
	}

	// Appending the Histograms 
	Histogram_None -> push_back(Jets_None);
	Histogram -> push_back(Jets_N);
}

void Stack_Generator(vector<TH1F*> *Hist_Vec, THStack *Stack, TLegend *Legend)
{
	vector<Color_t> Colors {kRed, kBlue, kOrange, kCyan, kGreen, kYellow, kViolet, kAzure};
	
	for (unsigned int x = 0; x <Hist_Vec -> size()-1; x++)
	{
		auto Hist1 = Hist_Vec -> at(x);
		cout << "Proccess: " << Hist1 -> GetTitle();
		cout << Hist1 -> Integral() << endl;
		Hist1 -> SetFillColor(Colors.at(x));
		Hist1 -> SetLineWidth(0);
		Legend -> AddEntry(Hist1);
		Stack -> Add(Hist1);
	}
}


void AIDA()
{
	const TString Path = "/home/tnom6927/Dokumente/Project/Analysis/Samples_by_Carl/"; 

	// Monte Carlo and Data sample sets.
	vector<string> List = {"MonteCarlo", "Data"};

	// Defining the relevant SM proccesses.
	vector<string> SM_Proccesses = {"Diboson", "ttbar", "ttV", "tW", "Wjets", "Zjets", "ttH", "Data"};

	// Defining the pointers for the SM proccesses of interest
	auto Histograms_NoJet = new vector<TH1F*>;
	auto Histograms_Jets = new vector<TH1F*>;
	
	for (unsigned int i = 0; i < SM_Proccesses.size(); i++)
	{
		auto ROOT_Files = new vector<string>;
		for ( unsigned int j=0; j < List.size(); j++)
		{
			Files(Path + TString(List.at(j)), SM_Proccesses.at(i), ROOT_Files);
		}

		// Calling the Graphing function that handles Histograms with selection rules	
		Graphing(Histograms_NoJet, Histograms_Jets, ROOT_Files, SM_Proccesses.at(i));
		
		// In loop clean out.
		delete ROOT_Files;
		ROOT_Files = NULL;
	}
	
	// Creating a new canvas pointer	
	TCanvas *Canv = new TCanvas("Canvas", "Canvas", 1600, 800);
	Canv -> Divide(2);
	Canv -> cd(1);	

	// Generating the Legend and the stack for the monte carlo histograms 
	THStack *Stacked_NoJet = new THStack("Stack_No_Jet", "0 jets Opposite Flavor - Opposite Charge");
	THStack *Stacked_Jet = new THStack("Stack_Jet", "N #geq 1 jets Opposite Flavor - Opposite Charge");
	
	// Generating a legend pointer 
	TLegend *Legend1 = new TLegend(0.68, 0.72, 0.98, 0.92);
	cout << "No jets in this event" << endl;
	Stack_Generator(Histograms_NoJet, Stacked_NoJet, Legend1);
	TLegend *Legend2 = new TLegend(0.68, 0.72, 0.98, 0.92);
	cout << "Jets in this event" << endl;
	Stack_Generator(Histograms_Jets, Stacked_Jet, Legend2);
	
	// Generating the Data Histograms 
	auto Data_NoJet = Histograms_NoJet -> at(Histograms_NoJet -> size()-1);
	Data_NoJet -> SetLineWidth(0);	
	auto Data_Jet = Histograms_Jets -> at(Histograms_Jets -> size()-1);
	Data_Jet -> SetLineWidth(0);	

	cout << "No Jet: "<< Data_NoJet -> Integral() << endl; 
	cout << "Jet: "<< Data_Jet -> Integral() << endl; 
	
	// Formating and drawing the histograms
	Stacked_NoJet -> Draw("HIST");
	Stacked_NoJet -> GetXaxis() -> SetTitle("Missing Energy (GeV)");
	Data_NoJet -> Draw("same H*");
	Legend1 -> AddEntry(Data_NoJet);
	Legend1 -> Draw();

	Canv -> cd(2);

	Stacked_Jet -> Draw("HIST");
	Stacked_Jet -> GetXaxis() -> SetTitle("Missing Energy (GeV)");
	Data_Jet -> Draw("same H*");
	Legend2 -> AddEntry(Data_Jet);
	Legend2 -> Draw();

	Canv -> Update();
}
