// Common classes for all server modules

#include <array>
#include <string>

using std::string;

constexpr char kStartPacket = '<';
constexpr char kEndPacket = '>';
constexpr int kArgumentLen = 4;
constexpr int kPayloadLen = 12;
constexpr int kCsumLen = 4;

enum class Action
{
	AddPart,
	AssignPart,
	ConfirmSorting,
	GetBinConfig,
	PartRanOffBelt,
	Handshake,
	GetStatus,
	SetParameters,
	FlushPartIndex,
	PrintFullPartIndex,
	PrintSinglePartIndex,
	OutputTest,
	PrintPartIndex,
	Acknowledge
};

struct Command
{
	Action m_action;
	string m_string;
};

const Command AddPart{ Action::AddPart, "A" };
const Command AssignPart{ Action::AssignPart, "B" };
const Command ConfirmSorting{ Action::ConfirmSorting, "C" };

class BbPacket
{
	//	<XAAAA123456789012CSUM>
	//	X = Command
	//	AAAA = Arguments
	//	123456789012 = payload
	//	CSUM = checksum

public:
	BbPacket(Command command, string& argument, string& payload) : m_command(command), m_argument(argument), m_payload(payload) {};
	string GetString();

private:
	void CalcCSUM();
	Command m_command;
	string m_argument;
	string m_payload;
	string m_CSUM;
};