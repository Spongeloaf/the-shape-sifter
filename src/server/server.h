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
#include <filesystem>

using namespace std::chrono_literals;
using std::filesystem::path;

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
	bool IsOK() const { return m_InitializeOK; };
	void ProcessActivePartList();
	int Main();
	void SendPartsListToSUIP();
	void PullPartsFromClients();
	void RegisterClients(ClientInterfaces& clients);
	spdlog::level::level_enum GetLogLevel() const { return m_logLevel; };
	string GetAssetPath() const { return m_assetPath.string(); };
	INIReader* GetIniReader() { return &m_iniReader; };

private:
	bool LoadConfig();
	bool CreateLogger();
	bool FindAssetPath();
	void ExecuteServerCommands();
	void HandleBBTell(CommandServer&);
	void HandleBBAck(CommandServer&);
	CommandBB CreateBBCommand(const Parts::PartInstance&);

	ClientInterfaces m_clients;
	PartList m_ActivePartList;
	path m_assetPath;
	path m_configPath;
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


