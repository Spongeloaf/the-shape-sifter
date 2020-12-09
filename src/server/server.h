#ifndef SERVER_H_E3C650C14FA146B6AA281A3CC17B52E2
#define SERVER_H_E3C650C14FA146B6AA281A3CC17B52E2

#include <vector>
#include "../common/ss_classes.h"
#include <thread>
#include <iostream>
#include <opencv2/core.hpp>

using namespace std::chrono_literals;

class Server
{
public:
	Server();
	bool IsOK();

	Parts::PartInstance m_photoPhilePartBin;
	spdlog::level::level_enum GetLogLevel() { return m_logLevel; };
	string GetAssetPath() { return m_assetPath; };
	INIReader* GetIniReader() { return &m_iniReader; };

private:
	bool LoadConfig();

	INIReader m_iniReader;
	bool m_InitializeOK;
	std::vector<Parts::PartInstance> m_ActivePartList;
	string m_assetPath = "C:\\Users\\peter\\Google Drive\\software_dev\\the_shape_sifter\\";
	string m_configPath = m_assetPath + "settings.ini";
	std::shared_ptr<spdlog::logger> m_logger;
	std::chrono::milliseconds m_BbPacketTimeout = 50ms;
	std::chrono::milliseconds m_ServerTickInterval = 32ms;
	spdlog::level::level_enum m_logLevel = spdlog::level::level_enum::err;
};

#endif // !SERVER_H_E3C650C14FA146B6AA281A3CC17B52E2


