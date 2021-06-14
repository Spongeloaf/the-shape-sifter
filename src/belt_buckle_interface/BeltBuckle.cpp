/*****************************************************************************************************
		This is the software interface for the conveyor belt controller.
		We differentiate the hardware belt buckle from this piece of software
		by calling the hardware the 'belt buckle', and this software 'belt buckle client'

		This client acts as a proxy only. It converts serial strings to part objects and vice versa.
		All logic relating to system operation is handled by the BB or server.
*****************************************************************************************************/

#include "BeltBuckle.h"
#include <RS232/rs232.h>
#include "../common/bb_utils.h"

BeltBuckle::BeltBuckle(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader)
		: ClientBase(logLevel, clientName, assetPath, iniReader) 
{
	m_ComPort = m_iniReader->GetInteger(m_clientName, "com_port", 1);
	m_BaudRate = m_iniReader->GetInteger(m_clientName, "baud_rate", 57600);
	m_mode = {'8', 'N', '1', 0};
	m_FlowCtrl = 0;
};

int BeltBuckle::Main()
{
	if (RS232_OpenComport(m_ComPort, m_BaudRate, &m_mode[0], m_FlowCtrl))
	{
		m_logger->error("Cannot open comport");
		return (1);
	}

	// RS232_PollComport() dumps all recieved characters, which may or may not contain a complete command. We will take
	// everything there is currently and append it to the RX Buffer, allowing commands to be recieved and handled over
	// multiple calls to ParseBuffer().
	std::array<unsigned char, kMaxBufferLen> tempBuffer;
	tempBuffer.fill('\0');
	while (true)
	{
		int nCharsRX = RS232_PollComport(m_ComPort, &tempBuffer[0], kMaxBufferLen);

		if (nCharsRX > 0)
		{
			ParseRxBuffer(tempBuffer);
		}

		// Make damn sure this is clean
		tempBuffer.fill('\0');

		// Send m_TxBuffer
		RS232_SendBuf(m_ComPort, &m_TxBuffer[0], m_TxBuffer.size());
	}

	return 0;
}

// Handles incoming characters from the serial buffer.
void BeltBuckle::ParseRxBuffer(std::array<unsigned char, kMaxBufferLen>& buffer)
{
// We decouple the recieve buffer from the program loop by appending everything recieved in this loop to a member buffer.
	for (auto& c : buffer)
	{
		switch (c)
		{
			case '[':
				// Packet initiator.
				m_RxBuffer.clear();
				m_RxBuffer.push_back(c);
				break;

			case ']':
				// Packet terminator.
				m_RxBuffer.push_back(c);
				DeserializeCommand();
				m_RxBuffer.clear();
				break;

			default:
				m_RxBuffer.push_back(c);

				// Should we receive more than (kRxCommandLen - 1) characters before a terminator, something is wrong, dump the string.
				if (m_RxBuffer.size() > (kRxCommandLen - 1))
					m_RxBuffer.clear();
				break;
		}
	}
}

// Convert serial strings into server commands
void BeltBuckle::DeserializeCommand()
{
	if (m_RxBuffer.size() != kRxCommandLen)
	{
		m_logger->error("Called BeltBuckle::DeserializeCommand() with invalid string length. Expected " +
										std::to_string(kRxCommandLen) + " but got " + std::to_string(m_RxBuffer.size()));
		return;
	}

	// Char indexes of a command:
	//
	// [ACK-Y-999-XXXXXXXXXXXX-CSUM]
	// -123-5-789-123456789012-4567-
	// |   <10   |   10+   |  20+  |

	CommandServer command;

	string strMessage = {char(m_RxBuffer.at(1)), char(m_RxBuffer.at(2)), char( m_RxBuffer.at(3))};
	if (strMessage == "ACK")
		command.messageType = MesgType::Acknowledge;
	
	else if (strMessage == "TEL")
		command.messageType = MesgType::Tell;
	else
	{
		m_logger->error("Bad message in BB packet: " + strMessage);
		return;
	}

	auto actionPair = BBActionMap.find(m_RxBuffer.at(5));
	if (actionPair != BBActionMap.end())
		command.action = actionPair->second;
	else
	{
		m_logger->error("Bad BBAction in packet. Action: " + std::to_string(m_RxBuffer.at(5)));
		return;
	}

	command.argument = {char(m_RxBuffer.at(7)), char(m_RxBuffer.at(8)), char(m_RxBuffer.at(9))};
	command.payload.insert(command.payload.begin(), m_RxBuffer.at(11), m_RxBuffer.at(22));

	PutPartInOutputBuffer(command);
}

// The server calls this method to retrieve commands from the belt buckle
void BeltBuckle::SendCommandsToServer(CommandServerList& commands)
{
	if (m_CommandServerLock.try_lock())
	{
		if (!m_CommandsForServer.empty())
		{
			for (auto& command : m_CommandsForServer)
			{
				commands.push_back(std::move(command));
			}
			m_CommandsForServer.clear();
		}
		m_CommandServerLock.unlock();
	}
}

// The server call this method to send parts to this client
void BeltBuckle::SendCommandsToBBClient(CommandBB& part)
{
	if (m_CommandBBLock.try_lock())
	{
		m_CommandsForBB.push_back(std::move(part));
		m_CommandBBLock.unlock();
	}
}

// Sends a command from the server to the belt buckle
void BeltBuckle::SerializeCommands() 
{
	for (auto& cmd : m_CommandsForBB)
	{
		string str = cmd.BuildSerialString();
		m_TxBuffer.insert(m_TxBuffer.end(), str.begin(), str.end());
		m_TxBuffer.push_back('\n');
	}
}

// The client calls this method to place commands in the output buffer, for retrieval by the server.
void BeltBuckle::PutPartInOutputBuffer(CommandServer& cmd)
{
	m_CommandServerLock.lock();
	m_CommandsForServer.push_back(std::move(cmd));
	m_CommandServerLock.unlock();
}
