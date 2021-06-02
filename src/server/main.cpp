// This is the Shape Sifter main loop.

#include "server.h"
#include "../suip/suip.h"
#include "../mt_mind/mt_mind.h"
#include "../classifist/Classifist.h"
#include "../belt_buckle_interface/BeltBuckle.h"
#include "../FileWriter/FileWriter.h"

int main()
{
	Server server = Server();
	if (!server.IsOK())
		return -1;

	INIReader* iniReader = server.GetIniReader();
	spdlog::level::level_enum logLevel = server.GetLogLevel();
	std::string assetPath = server.GetAssetPath();

	PhotoPhile phile{logLevel, kNamePhotophile, assetPath, iniReader};
	std::thread threadPhile(&PhotoPhile::Main, &phile);
	
	MtMind mtm{logLevel, kNameMtMind, assetPath, iniReader};
	std::thread threadMtMind(&MtMind::Main, &mtm);

	Classifist cf{logLevel, kNameClassiFist, assetPath, iniReader};
	std::thread threadCF(&Classifist::Main, &cf);

	BeltBuckle bb{logLevel, kNameBeltBuckle, assetPath, iniReader};
	std::thread threadBB(&BeltBuckle::Main, &bb);

	FileWriter fw{ logLevel, kNameFileWriter, assetPath, iniReader };
	std::thread threadFW(&FileWriter::Main, &fw);

	SUIP suip{logLevel, kNameSUIP, assetPath, iniReader};

	// Start the server thread
	ClientInterfaces clients{&phile, &suip, &mtm, &cf, &bb};
	server.RegisterClients(clients);
	std::thread threadServer(&Server::Main, &server);

	return suip.Main();
}