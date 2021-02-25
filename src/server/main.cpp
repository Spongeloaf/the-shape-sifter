// This is the Shape Sifter main loop.

#include "server.h"
#include "../suip/suip.h"

int main()
{
	Server server = Server();
	if (!server.IsOK())
		return -1;

	// TODO: This is kind of a hack. I should find a better way to create only a photophile or a simulator.
	string sPhotophileName = "PhotoPhile";
	string sPhotophileSimName = "PhotoPhileSim";
	string sSuipName = "PhotoPhileSim";

	INIReader* iniRead = server.GetIniReader();

	// bool simulatePhotoPhile = iniRead->GetBoolean(sPhotophileName, "simulation", false);
	//
	// PhotoPhile* phile = nullptr;
	// std::thread* threadPhile = nullptr;

	// PhotophileSimulator* phileSim = nullptr;
	// std::thread* threadPhileSim = nullptr;

	// if (simulatePhotoPhile)
	//{
	//	phileSim = new PhotophileSimulator{ server.GetLogLevel(), sPhotophileSimName, server.GetAssetPath(),
	//server.GetIniReader() }; 	threadPhileSim = new std::thread(&PhotophileSimulator::Main, &phileSim);
	//}
	// else
	//{
	//	phile = new PhotoPhile{ server.GetLogLevel(), sPhotophileName, server.GetAssetPath(), server.GetIniReader() };
	//	threadPhile = new std::thread(&PhotoPhile::Main, &phile);
	//}

	PhotoPhile phile{server.GetLogLevel(), sPhotophileName, server.GetAssetPath(), server.GetIniReader()};
	std::thread threadPhile(&PhotoPhile::Main, &phile);


	SUIP suip{server.GetLogLevel(), sSuipName, server.GetAssetPath(), server.GetIniReader()};

	// Start the server thread
	ClientInterfaces clients{&phile, nullptr, &suip};
	server.RegisterClients(clients);
	std::thread threadServer(&Server::Main, &server);

	return suip.Main();
}