// Common classes for all Shape Sifter modules
#pragma once

#include <array>
#include <string>
#include <chrono>
#include <opencv2/core.hpp>

using std::string;

constexpr std::chrono::milliseconds kUpdateInterval(32);
constexpr char kStartPacket = '<';
constexpr char kEndPacket = '>';
constexpr int kArgumentLen = 4;
constexpr int kPayloadLen = 12;
constexpr int kCsumLen = 4;

namespace BeltBuckleInterface
{
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
}	// BeltBuckleInterface

enum class ServerMode
{
	run,
	idle,
};


namespace Parts
{
	typedef std::chrono::steady_clock::time_point timePoint;
	typedef int image;

	enum class ServerStatus
	{
		waitMTM,
		MTMDone,
		waitCF,
		cfDone,
		waitSort,
		sortDone,
		lost
	};

	enum class PartStatus
	{
		newPart,
		waitAck,
		tracked,
		assigned,
		sorted,
		lost
	};

	class PartInstance
	{
		PartInstance(string ID, timePoint captureTime, image img) : m_ID(ID),  m_TimeCaptured(captureTime), m_Image(img) {};

		string m_ID;
		string m_PartNumber;
		string m_CategoryNumber;
		string m_CategoryName;
		image m_Image;
		unsigned int m_BinNumber;
		int m_CameraOffset;
		ServerStatus m_ServerStatus;
		PartStatus m_PartStatus;
		timePoint m_TimeCaptured;
		timePoint m_TimeTaxi;
		timePoint m_TimeCF;
		timePoint m_TimeAdded;
		timePoint m_TimeAssigned;
	};
};	// namespace Parts