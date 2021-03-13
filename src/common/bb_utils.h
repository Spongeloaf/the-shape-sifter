// Structs and enums to support the belt buckle <--> server interface

#ifndef BB_UTILS_H
#define BB_UTILS_H

#include <string>

using std::string;

enum class BBmesg
{
	Acknowledge,
	Notify
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

// A command sent from the server to the belt buckle
struct CommandBB
{
	BBAction m_action;
	string m_Argument;
	string payload;
};

// A command sent from the belt buckle to the server
struct CommandServer
{
	BBmesg message;
	BBAction action;
	string argument;
	string payload;
};


using CommandServerList = std::vector<CommandServer>;

// Stores the char associated with a BBAction
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

#endif  // !BB_UTILS_H
