/*****************************************************************************************************
    This is the software interface for the conveyor belt controller.
    We differentiate the hardware belt buckle from this piece of software
    by calling the hardware the 'belt buckle', and this software 'belt buckle client'

    This client acts as a proxy only. It converts serial strings to part objects and vice versa.
    All logic relating to system operation is handled by the BB or server.
*****************************************************************************************************/

#ifndef BELTBUCKLE_H
#define BELTBUCKLE_H

#include "../common/ss_classes.h"
#include "../common/bb_utils.h"
#include <vector>

// Max serial buffer length in windows -1
const unsigned int kMaxBufferLen = 4096;
const unsigned int kRxCommandLen = 29;


class BeltBuckle : public ClientBase
{
public:
	BeltBuckle(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader);
	int Main();
	void SendCommandsToServer(CommandServerList& commands);
	void SendCommandsToBBClient(CommandBB& part);

private:
	void ParseRxBuffer(std::array<unsigned char, kMaxBufferLen>& buffer);
	void DeserializeCommand();
	void SerializeCommands();
	void PutPartInOutputBuffer(CommandServer& cmd);
 
	std::vector<unsigned char> m_RxBuffer;
	std::vector<unsigned char> m_TxBuffer;

  int m_BaudRate;
	int m_ComPort;
	std::array<char, 4> m_mode;
	int m_FlowCtrl;
	
	std::mutex m_CommandServerLock;
	std::mutex m_CommandBBLock;
	CommandServerList m_CommandsForServer;
	CommandBBList m_CommandsForBB;

};

#endif  // !BELTBUCKLE_H