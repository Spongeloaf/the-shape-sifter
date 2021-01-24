// This is the Shape Sifter server.

#include "server.h"


// Execution Entry point
int main()
{
	Server server = Server();
	if (!server.IsOK())
		return -1;

	// HANDLE myHandle = CreateThread(0, 0, RunPhotophile, &server.m_photoPhilePartBin; , 0, &myThreadID;);
	//ClientConfig phileCfg{ server.GetLogLevel(), "PhotoPhile", server.GetAssetPath(), server.GetIniReader() };
	ClientConfig phileSimCfg{ server.GetLogLevel(), "PhotoPhileSim", server.GetAssetPath(), server.GetIniReader() };

	// TODO: This is kind of a hack. I should find a better way to creaate only a photophilr or a simulator.
	//PhotoPhile phile(phileCfg);
	PhotophileSimulator phileSim(phileSimCfg);
	std::thread threadPhileSim(&PhotophileSimulator::Main, &phileSim);
	//std::thread threadPhile(&PhotoPhile::Main, &phile);
	ClientInterfaces clients{ nullptr, &phileSim };

	server.Main(clients);
}

Server::Server()
{
	m_iniReader = INIReader(m_configPath);
	m_InitializeOK = LoadConfig();
}

bool Server::IsOK()
{
	return m_InitializeOK;
}

bool Server::LoadConfig()
{
	// setup logger
	try
	{
		// Create basic file logger (not rotated)
		m_logger = spdlog::basic_logger_mt("serverLogger", "server.log", true /* delete old logs */);
		m_logger->set_level(spdlog::level::info);
		m_logger->info("Server online");
		m_logger->flush();
	}
	catch (const spdlog::spdlog_ex& ex)
	{
		std::cout << "Log initialization failed: " << ex.what() << std::endl;
	}
	
	if (m_iniReader.ParseError() != 0)
	{
		assert(!"Could not load config file! Aborting.");
		m_logger->critical("Could not load config file: {}", m_configPath);
		return false;
	}

	m_BbPacketTimeout = std::chrono::milliseconds(m_iniReader.GetInteger("server", "bb_ack_timeout", -1));
	m_ServerTickInterval = std::chrono::milliseconds(m_iniReader.GetInteger("server", "global_tick_rate", -1));
	m_PhotophileSimulator = m_iniReader.GetBoolean("server", "photophileSimulator", false);

	return true;
}

int Server::Main(ClientInterfaces clients)
{
	
	//	# 3rd party imports
	//import time
	//
	//# 1st party imports. Safe to use from x import *
	//import ss_classes
	//import ss_server_lib as slib
	//
	//
	//# needed for multiprocessing
	//if __name__ == '__main__':
	//
	//    init = ss_classes.ServerInit()
	//    clients, bb = init.start_clients()
	//    mode = ss_classes.ServerMode()
	//    server = slib.Server(init, bb)
	//

	// main loop
	while (true)
	{
		// loop timer
		auto start = std::chrono::system_clock::now();
		
		if (clients.phileSim)
			clients.phileSim->GetParts(m_ActivePartList);
		//
		//if mode.check_mtm:
		//    server.check_mtm()
		//
		//if mode.check_cf:
		//    server.check_cf()
		//
		//if mode.check_bb:
		//    server.check_bb()
		//
		//if mode.iterate_active_part_db:
		//    server.iterate_part_list()
		//
		//server.check_suip(mode)
		//server.send_part_list_to_suip()
		//
		// global_tick_rate is the time in milliseconds of each loop, taken from settings.ini
		auto end = std::chrono::system_clock::now();
		std::chrono::duration<double, std::milli> elapsed = end - start;

		if (elapsed > kLockTimeout)
		{
			m_logger->debug("Took too long to lock a thread. Milliseconds: {}", elapsed.count());
		}

		if (elapsed < kUpdateInterval)
		{
			start = std::chrono::system_clock::now();
			std::this_thread::sleep_for(kUpdateInterval - elapsed);
			end = std::chrono::system_clock::now();
			std::chrono::duration<double, std::milli> elapsed = end - start;
		}

	}
}