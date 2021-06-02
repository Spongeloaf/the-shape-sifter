#ifndef SERVER_H_E3C650C14FA146B6AA281A3CC17B52E2
#define SERVER_H_E3C650C14FA146B6AA281A3CC17B52E2

#include <vector>
#include "../common/ss_classes.h"
#include <thread>
#include <iostream>
#include <opencv2/core.hpp>
#include "../photophile/photophile.h"
#include "../suip/suip.h"
#include "../mt_mind/mt_mind.h"
#include "../belt_buckle_interface/BeltBuckle.h"

using namespace std::chrono_literals;

struct ClientInterfaces
{
	ClientBase* phile;
	ClientBase* suip;
	ClientBase* mtm;
	ClientBase* cf;
	BeltBuckle* bb;
	ClientBase* fw;
};

class Server
{
public:
	Server();
	bool IsOK();
	void ProcessActivePartList();
	int Main();
	void SendPartsListToSUIP();
	void PullPartsFromClients();
	void thing();
	void OverrideClients(ClientInterfaces);
	void RegisterClients(ClientInterfaces& clients);
	spdlog::level::level_enum GetLogLevel() { return m_logLevel; };
	string GetAssetPath() { return m_assetPath; };
	INIReader* GetIniReader() { return &m_iniReader; };

private:
	bool LoadConfig();
	void ExecuteServerCommands();
	void HandleBBTell(CommandServer&);
	void HandleBBAck(CommandServer&);
	CommandBB CreateBBCommand(const Parts::PartInstance&);

	ClientInterfaces m_clients;
	PartList m_ActivePartList;
	string m_assetPath = "C:\\Users\\peter.vandergragt\\Google Drive\\software_dev\\the_shape_sifter\\"; // TODO: Ugh. Need to fix this.
	string m_configPath = m_assetPath + "settings.ini";
	INIReader m_iniReader;
	bool m_InitializeOK;
	bool m_PhotophileSimulator;
	std::shared_ptr<spdlog::logger> m_logger;
	std::chrono::milliseconds m_BbPacketTimeout = 50ms;
	std::chrono::milliseconds m_ServerTickInterval = 32ms;
	spdlog::level::level_enum m_logLevel = spdlog::level::level_enum::err;
	CommandServerList m_CommandsForServer;
	CommandServerList m_CommandsForBB;
};

#endif // !SERVER_H_E3C650C14FA146B6AA281A3CC17B52E2


