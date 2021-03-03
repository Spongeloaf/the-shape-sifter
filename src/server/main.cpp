// This is the Shape Sifter main loop.

#include "server.h"
#include "../suip/suip.h"
#include "../mt_mind/mt_mind.h"

int main()
{
	Server server = Server();
	if (!server.IsOK())
		return -1;

	// TODO: This is kind of a hack. I should find a better way to create only a photophile or a simulator.
	string sPhotophileName = "PhotoPhile";
	string sPhotophileSimName = "PhotoPhileSim";
	string sSuipName = "SUIP";
	string sMtMindName = "MtMind";

	INIReader* iniRead = server.GetIniReader();

	PhotoPhile phile{server.GetLogLevel(), sPhotophileName, server.GetAssetPath(), server.GetIniReader()};
	std::thread threadPhile(&PhotoPhile::Main, &phile);
	
	MtMind mtm{server.GetLogLevel(), sMtMindName, server.GetAssetPath(), server.GetIniReader()};
	std::thread threadMtMind(&MtMind::Main, &mtm);

	SUIP suip{server.GetLogLevel(), sSuipName, server.GetAssetPath(), server.GetIniReader()};

	// Start the server thread
	ClientInterfaces clients{&phile, &suip, &mtm};
	server.RegisterClients(clients);
	std::thread threadServer(&Server::Main, &server);

	return suip.Main();
}