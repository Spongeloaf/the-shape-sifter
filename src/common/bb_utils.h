// Structs and enums to support the belt buckle <--> server interface

#ifndef BB_UTILS_H
#define BB_UTILS_H

#include <string>

// Forward declarations
struct CommandServer;
struct CommandBB;
enum class MesgType;
enum class BBAction;

using std::string;
using CommandServerList = std::vector<CommandServer>;

enum class MesgType
{
	Acknowledge,
	Tell
};

enum class BBAction
{
	AddPart,
	AssignPartToBin,
	ConfirmSorting,
	GetBinConfig,
	PartRanOffBelt,
	PrintEncoderDistance,
	Handshake,
	GetStatus,
	SetParameters,
	FlushPartIndex,
	PrintFullPartIndex,
	PrintSinglePartIndex,
	OutputTest,
	PrintPartIndex,
};

// For easy conversion from action enum to string
static const std::map<string, MesgType> BBmesgTypeMap = {
		{"ACK", MesgType::Acknowledge},
		{"TEL", MesgType::Tell}
};

// For easy conversion from action enum to string
static const std::map<char, BBAction> BBActionMap = {
		{'A', BBAction::AddPart},
		{'B', BBAction::AssignPartToBin},
		{'C', BBAction::ConfirmSorting},
		{'D', BBAction::GetBinConfig},
		{'F', BBAction::PartRanOffBelt},
		{'G', BBAction::PrintEncoderDistance},
		{'H', BBAction::Handshake},
		{'I', BBAction::GetStatus},
		{'M', BBAction::SetParameters},
		{'O', BBAction::FlushPartIndex},
		{'P', BBAction::PrintFullPartIndex},
		{'S', BBAction::PrintSinglePartIndex},
		{'T', BBAction::OutputTest}
};

// A command sent from the server to the belt buckle
struct CommandBB
{
	BBAction action;
	string argument;
	string payload;

	string BuildSerialString()
	{
		// Example serial command from the server to the belt buckle:
		// <XAAAA123456789012CSUM>

		string sAction = "ERROR";
		for (auto& a : BBActionMap)
		{
			if (a.second == action)
			{
				sAction = a.first;
				break;
			}
		}

		return "<" + sAction + argument + payload + "CSUM>";
	}
};

// A command sent from the belt buckle to the server
struct CommandServer
{
	MesgType messageType = MesgType::Tell;
	BBAction action = BBAction::Handshake;
	string argument = "";
	string payload = "";

	string BuildSerialString() 
	{
		// Example serial command from the belt buckle to the server: 
		// [ACK-Y-999-XXXXXXXXXXXX-CSUM]

		string sType = "ERROR";
		switch (messageType)
		{
			case MesgType::Tell:
				sType = "TEL";
				break;
			case MesgType::Acknowledge:
				sType = "ACK";
		}

		string sAction = "ERROR";
		for (auto& a : BBActionMap)
		{
			if (a.second == action)
			{
				sAction = a.first;
				break;
			}
		}

		return "[" + sType + "-" + sAction + "-" + payload + "-CSUM]";
	}
};



#endif  // !BB_UTILS_H
