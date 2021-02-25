// Common classes for all Shape Sifter modules
#ifndef SS_CLASSES_H_11205B5C8C7047CAAA518874BA2C272C
#define SS_CLASSES_H_11205B5C8C7047CAAA518874BA2C272C

#include <array>
#include <string>
#include <chrono>
#include <opencv2/core.hpp>
#include <INIReader/INIReader.h>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h> 
#include <thread>
#include <mutex>
#include <iostream>

using std::string;
constexpr std::chrono::duration<double, std::milli> kUpdateInterval(10);
constexpr std::chrono::duration<double, std::milli> kLockTimeout(kUpdateInterval * 10);
constexpr unsigned int kPUIDLength = 12;
constexpr char kStartPacket = '<';
constexpr char kEndPacket = '>';
constexpr int kArgumentLen = 4;
constexpr int kPayloadLen = kPUIDLength;
constexpr int kCsumLen = 4;
constexpr int kPartTableRows = 64;
constexpr int kPartTableColumns = 13;

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

namespace Parts
{
	enum class ServerStatus
	{
		newPart,
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

	struct PartInstance
	{
		PartInstance(){};

		PartInstance(string ID, std::chrono::system_clock::time_point captureTime, cv::Mat img) :
			m_ID(ID), 
			m_PartNumber(""),
			m_CategoryNumber(""),
			m_CategoryName(""),
			m_Image(img),
			m_BinNumber(0),
			m_CameraOffset(0),
			m_ServerStatus(ServerStatus::newPart),
			m_PartStatus(PartStatus::newPart),
			m_TimeCaptured(captureTime),
			m_TimeTaxi(captureTime),
			m_TimeCF(captureTime),
			m_TimeAdded(captureTime),
			m_TimeAssigned(captureTime)
		{};

		PartInstance(const PartInstance& part) :
			m_ID (part.m_ID),
			m_BinNumber(part.m_BinNumber),
			m_CameraOffset(part.m_CameraOffset),
			m_PartNumber(part.m_PartNumber),
			m_CategoryNumber(part.m_CategoryNumber),
			m_CategoryName(part.m_CategoryName),
			m_Image(part.m_Image),
			m_ServerStatus(part.m_ServerStatus),
			m_PartStatus(part.m_PartStatus),
			m_TimeCaptured(part.m_TimeCaptured),
			m_TimeTaxi(part.m_TimeTaxi),
			m_TimeCF(part.m_TimeCF),
			m_TimeAdded(part.m_TimeAdded),
			m_TimeAssigned(part.m_TimeAssigned)
		{};

		string m_ID;
		cv::Mat m_Image;
		unsigned int m_BinNumber;
		int m_CameraOffset;
		ServerStatus m_ServerStatus;
		PartStatus m_PartStatus;
		string m_PartNumber;
		string m_CategoryNumber;
		string m_CategoryName;
		std::chrono::system_clock::time_point m_TimeCaptured;
		std::chrono::system_clock::time_point m_TimeTaxi;
		std::chrono::system_clock::time_point m_TimeCF;
		std::chrono::system_clock::time_point m_TimeAdded;
		std::chrono::system_clock::time_point m_TimeAssigned;
	};

};	// namespace Parts

using PartList = std::unordered_map<string, Parts::PartInstance>;

class ClientBase
{
public:
	virtual int Main() = 0;
	void SendPartsToServer(PartList& partList);
	void SendPartsToCLient(Parts::PartInstance& partList);

	ClientBase(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader) :
		m_logLevel(logLevel), 
		m_clientName(clientName),
		m_assetPath(assetPath),
		m_iniReader(iniReader),
		m_isOk(false)
		{
			// Create basic file logger (not rotated)
			m_logger = spdlog::basic_logger_mt(m_clientName, "\\log\\" + m_clientName + ".log", true /* delete old logs */);
			m_logger->set_level(spdlog::level::info);
			m_logger->info(m_clientName + " online");
			m_logger->flush();
		};

protected:
	spdlog::level::level_enum m_logLevel;
	string m_clientName;
	string m_assetPath;
	INIReader* m_iniReader;
	bool m_isOk;
	std::shared_ptr<spdlog::logger> m_logger;
	std::mutex m_OutputLock;
	std::mutex m_InputLock;
	PartList m_OutputBuffer;
	PartList m_InputBuffer;
};

#endif // !SS_CLASSES_H_11205B5C8C7047CAAA518874BA2C272C