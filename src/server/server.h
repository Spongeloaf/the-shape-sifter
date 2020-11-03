#pragma once

#include <vector>
#include "../common/ss_classes.h"
#include <INIReader/INIReader.h>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h> 
#include <chrono>
#include <thread>
#include <iostream>
#include "../common/ss_classes.h"

using namespace std::chrono_literals;

class Server
{
public:
	Server();
	bool IsOK();

private:
	bool LoadConfig();

	bool m_InitializeOK;
	std::vector<Parts::PartInstance> m_ActivePartList;
	string m_assetPath = "C:\\Users\\peter\\Google Drive\\software_dev\\the_shape_sifter";
	string m_configPath =  m_assetPath + "\\settings.ini";
	std::shared_ptr<spdlog::logger> m_logger;
	std::chrono::milliseconds m_BbPacketTimeout = 50ms;
	std::chrono::milliseconds m_ServerTickInterval = 32ms;

};