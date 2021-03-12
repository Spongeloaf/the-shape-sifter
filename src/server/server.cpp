// This is the Shape Sifter server.

#include "server.h"

Server::Server()
{
	m_iniReader = INIReader(m_configPath);
	m_InitializeOK = LoadConfig();
}

bool Server::IsOK()
{
	return m_InitializeOK;
}

void Server::RegisterClients(ClientInterfaces& clients)
{
	m_clients = clients;
};

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

int Server::Main()
{
	// If any ptrs are null, you should check to see if you called RegisterClients() before main(), and ensure you've setup
	// threads for each client in main.cpp::main()
	if (!(m_clients.phile && m_clients.mtm && m_clients.suip && m_clients.cf))
		return 1;

	// main loop
	while (true)
	{
		// loop timer
		auto start = std::chrono::system_clock::now();
		
		m_clients.phile->SendPartsToServer(m_ActivePartList);
		m_clients.mtm->SendPartsToServer(m_ActivePartList);
		m_clients.cf->SendPartsToServer(m_ActivePartList);

		for (auto& part : m_ActivePartList)
		{
			switch (part.second.m_ServerStatus)
			{
				case Parts::ServerStatus::newPart:
					// TODO: Need to dispatch to BB
					part.second.m_PartStatus = Parts::PartStatus::waitAckAdd;
					part.second.m_ServerStatus = Parts::ServerStatus::waitMTM;
					m_clients.mtm->SendPartsToClient(part.second);
					break;
				
				case Parts::ServerStatus::MTMDone:
					part.second.m_ServerStatus = Parts::ServerStatus::waitCF;
					m_clients.cf->SendPartsToClient(part.second);
					break;

				case Parts::ServerStatus::cfDone:
					part.second.m_ServerStatus = Parts::ServerStatus::cfDone;
					part.second.m_PartStatus = Parts::PartStatus::waitAckAssign;
					m_clients.bb->SendPartsToClient(part.second);
					break;

				case Parts::ServerStatus::sortDone:
					// sort done 
					break;
			}
		}

		m_clients.suip->CopyServerPartListToClient(m_ActivePartList);

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
