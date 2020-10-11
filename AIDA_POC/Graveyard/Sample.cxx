void Sample()
{
	// Defining the path to the ntuples 
	const TString Path = "/sydpp2/atlas/sgtop/ntuple4/";
	void *Open_Dir = gSystem -> OpenDirectory(Path);

	// creating a string vector with the proccess of interest
	vector<string> Process = {"tW"};

	// Declaring the Filename variable 
	Char_t *Filename;
	
	// Declaring a vector of type string for the file directory of the processes 
	vector<string> Directories;
		
	// Reading the files in the file directory
	while ((Filename = (Char_t*) gSystem -> GetDirEntry(Open_Dir)))
	{
		// Iterating through the processes in the vector 
		for (auto i : Process)
		{
			// Changing file type
			string FileString = Filename;
			
			// Checking if the string is within the filename
			if (FileString.find(i) != std::string::npos)
			{
				Directories.push_back(FileString);
			}
		}
	}

	// Clearing out pointers
	delete Filename;
	Open_Dir = NULL; 

	// Initializing the TChain class
	TChain Chain("WtLoop_nominal");
	
	// looping over the Directories vector and adding in the files to the chain 
	for (auto i : Directories)
	{
		std::cout << i << std::endl;
		Chain.Add((string(Path) + i).c_str());
	}

	// Reading just the MET from the chain
	TTreeReader Reader(&Chain);
	TTreeReaderValue<float> MET(Reader, "met");
	TTreeReaderValue<float> Weight(Reader, "weight_nominal");

	// Defining the number of bins and the maximum missing ET threshold 
	float Energy_Threshold = 250; // GeV
	int Bins = 20; // Number of bins 
	float Luminosity = 140.5; // Measured luminosity

	// Creating histogram objects
	auto Histogram_Simulation = new TH1F("Monte Carlo", "MonteCarlo", Bins, 0, Energy_Threshold);

	while (Reader.Next())
	{
		float Missing_ET = *MET; // Dereferencing the pointer
		float Nominal = *Weight; // Event weighting 
	
		// Making sure the data doesnt leak above the threshold 
		if (Missing_ET > Energy_Threshold)
		{
			Missing_ET = Energy_Threshold-1;		
		}

		// Filling the histogram with the data
		Histogram_Simulation -> Fill(Missing_ET, Nominal*Luminosity); 
	}
	
	TH1F *Fake_Data = (TH1F*)Histogram_Simulation -> Clone("hnew");
	Fake_Data -> FillRandom("gaus", 1000);

	// Getting the size of the histogram bin
	Double_t bin = Histogram_Simulation -> GetBinContent(1);
		
	// Making two copies of the histograms to create the systematics 
	TH1F *Upper_System = (TH1F*)Histogram_Simulation -> Clone("hnew");
	TH1F *Lower_System = (TH1F*)Histogram_Simulation -> Clone("hnew");

	// Replacing the bin content of the copied histograms 
	Upper_System -> SetBinContent(1, 2*bin);
	Lower_System -> SetBinContent(1, 0.5*bin);
	
	bool Debug = false;

	if (not Debug)
	{
		// Creating a new root file to write the histograms to 
		TFile *Output = new TFile("Inputs/sig.root", "RECREATE");
		Histogram_Simulation -> Write("Wt");
		Upper_System -> Write("Wt_U_Sys");
		Lower_System -> Write("Wt_L_Sys");
		Output -> Close();	
	
		TFile *Data = new TFile("Inputs/data.root", "NEW");
		Fake_Data -> Write("Wt");
		Data -> Close();
	}
	else 
	{
		// Part of the debug
		TCanvas *Canvas = new TCanvas("Canvas", "Canvas", 1600, 800);
		Canvas -> Divide(4);
		Canvas -> cd(1);
		Histogram_Simulation -> SetFillColor(kBlue);
		Histogram_Simulation -> Draw("HIST");

		Canvas -> cd(2);
		Fake_Data -> SetTitle("Data");
		Fake_Data -> Draw("HIST*");
	
		Canvas -> cd(3);
		Upper_System -> SetTitle("Upper Systematic");
		Upper_System -> Draw("HIST");

		Canvas -> cd(4);
		Lower_System -> SetTitle("Lower Systematic");
		Lower_System -> Draw("HIST");



	}

	return 0;
}
