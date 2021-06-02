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

// Executes commands sent from clients
void Server::ExecuteServerCommands() 
{
	for (auto command : m_CommandsForServer)
	{
		switch (command.messageType)
		{
			case MesgType::Acknowledge:
				HandleBBAck(command);
				break;

			case MesgType::Tell:
				HandleBBTell(command);
				break;
			default:
				// Should never get here! Did you add a message type enum and forget to catch it here?
				m_logger->error("Failure in ExecuteServerCommands() command: " + command.BuildSerialString());
		}
	}
}

// Handles "TEL" comamnds sent from the belt buckle to the server
void Server::HandleBBTell(CommandServer& command)
{
	try
	{
		switch (command.action)
		{
			case BBAction::ConfirmSorting:
				m_ActivePartList[command.payload].m_BBStatus = Parts::BBStatus::Sorted;
				m_ActivePartList[command.payload].m_ServerStatus = Parts::ServerStatus::sortDone;
				break;

			case BBAction::PartRanOffBelt:
				m_ActivePartList[command.payload].m_BBStatus = Parts::BBStatus::Lost;
				m_ActivePartList[command.payload].m_ServerStatus = Parts::ServerStatus::Lost;
				break;

			case BBAction::AddPart:
			case BBAction::AssignPartToBin:
			case BBAction::GetBinConfig:
			case BBAction::PrintEncoderDistance:
			case BBAction::Handshake:
			case BBAction::GetStatus:
			case BBAction::SetParameters:
			case BBAction::FlushPartIndex:
			case BBAction::PrintFullPartIndex:
			case BBAction::PrintSinglePartIndex:
			case BBAction::OutputTest:
				// do nothing
				break;

			default:
				// Should never get here! Did you add a message type enum and forget to catch it here?
				m_logger->error("Failure in HandleBBTell() command: " + command.BuildSerialString());
		}
	}
	catch (...)
	{
		m_logger->error("Exception in HandleBBTell(). Command: " + command.BuildSerialString());
	}
}

// Handles "ACK" comamnds sent from the belt buckle to the server
void Server::HandleBBAck(CommandServer& command)
{
	try
	{
		switch (command.action)
		{
			case BBAction::AddPart:
				m_ActivePartList[command.payload].m_BBStatus = Parts::BBStatus::Added;
				break;
			case BBAction::AssignPartToBin:
				m_ActivePartList[command.payload].m_BBStatus = Parts::BBStatus::Assigned;
				break;

			case BBAction::ConfirmSorting:
			case BBAction::GetBinConfig:
			case BBAction::PartRanOffBelt:
			case BBAction::PrintEncoderDistance:
			case BBAction::Handshake:
			case BBAction::GetStatus:
			case BBAction::SetParameters:
			case BBAction::FlushPartIndex:
			case BBAction::PrintFullPartIndex:
			case BBAction::PrintSinglePartIndex:
			case BBAction::OutputTest:
				// do nothing
				break;

			default:
				// Should never get here! Did you add a message type enum and forget to catch it here?
				m_logger->error("Failure in HandleBBAck() command: " + command.BuildSerialString());
		}
	}
	catch (...)
	{
		m_logger->error("Exception in HandleBBAck(). Command: " + command.BuildSerialString());
	}
}

CommandBB Server::CreateBBCommand(const Parts::PartInstance& part)
{
	CommandBB cmd;
	cmd.payload = part.m_PUID;

	switch (part.m_ServerStatus)
	{
		case Parts::ServerStatus::newPart:
			cmd.action = BBAction::AddPart;
			cmd.argument = "0000";
			break;

		case Parts::ServerStatus::cfDone:
			cmd.action = BBAction::AssignPartToBin;
			cmd.IntToArgumentString(part.m_BinNumber);
			break;
	}
	return std::move(cmd);
}

void Server::ProcessActivePartList()
{
	for (auto& part : m_ActivePartList)
	{
		switch (part.second.m_ServerStatus)
		{
			case Parts::ServerStatus::newPart:
				// TODO: Need to dispatch to BB
				part.second.m_BBStatus = Parts::BBStatus::waitAckAdd;
				part.second.m_ServerStatus = Parts::ServerStatus::waitMTM;
				m_clients.mtm->SendPartToClient(part.second);
				m_clients.bb->SendCommandsToBBClient(CreateBBCommand(part.second));
				m_clients.fw->SendPartToClient(part.second);
				break;

			case Parts::ServerStatus::MTMDone:
				part.second.m_ServerStatus = Parts::ServerStatus::waitCF;
				m_clients.cf->SendPartToClient(part.second);
				break;

			case Parts::ServerStatus::cfDone:
				part.second.m_ServerStatus = Parts::ServerStatus::cfDone;
				part.second.m_BBStatus = Parts::BBStatus::waitAckAssign;
				m_clients.bb->SendPartToClient(part.second);
				m_clients.bb->SendCommandsToBBClient(CreateBBCommand(part.second));

				break;

			case Parts::ServerStatus::Lost:
				m_ActivePartList.erase(part.first);
				break;

			case Parts::ServerStatus::sortDone:
				m_ActivePartList.erase(part.first);
				break;
		}
	}
}

int Server::Main()
{
	// If any ptrs are null, you should check to see if you called RegisterClients() before main(), and ensure you've setup
	// threads for each client in main.cpp::main()
	if (!(m_clients.phile && m_clients.mtm && m_clients.suip && m_clients.cf && m_clients.bb))
		return 1;

	// main loop
	while (true)
	{
		// loop timer
		auto start = std::chrono::system_clock::now();
		
		PullPartsFromClients();
		ProcessActivePartList();
		ExecuteServerCommands();
		SendPartsListToSUIP();

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

void Server::SendPartsListToSUIP()
{
	m_clients.suip->CopyServerPartListToClient(m_ActivePartList);
}

void Server::PullPartsFromClients()
{
	m_clients.phile->SendPartsToServer(m_ActivePartList);
	m_clients.mtm->SendPartsToServer(m_ActivePartList);
	m_clients.cf->SendPartsToServer(m_ActivePartList);
	m_clients.bb->SendCommandsToServer(m_CommandsForServer);
}

/*
string Server::GetAssetPath() 
{
	/* Convert this to c++
	string dbFilePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
																	 "Google\\Drive\\sync_config.db");

	string csGdrive = @"Data Source=" + dbFilePath + ";Version=3;New=False;Compress=True;";

	try
	{
		using(var con = new SQLiteConnection(csGdrive))
		{
			con.Open();
			using(var sqLitecmd = new SQLiteCommand(con))
			{
				// To retrieve the folder use the following command text
				sqLitecmd.CommandText = "select * from data where entry_key='local_sync_root_path'";

				using(var reader = sqLitecmd.ExecuteReader())
				{
					reader.Read();
					// String retrieved is in the format "\\?\<path>" that's why I have used Substring function to extract the
					// path alone.
					destFolder = reader["data_value"].ToString().Substring(4);
					Console.WriteLine("Google Drive Folder: " + destFolder);
				}
			}
		}
	}
}
*/