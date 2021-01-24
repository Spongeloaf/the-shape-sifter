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

using std::string;

constexpr std::chrono::duration<double, std::milli> kUpdateInterval(10);
constexpr std::chrono::duration<double, std::milli> kLockTimeout(100);
constexpr int kPUIDLength = 12;
constexpr char kStartPacket = '<';
constexpr char kEndPacket = '>';
constexpr int kArgumentLen = 4;
constexpr int kPayloadLen = kPUIDLength;
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
	typedef std::chrono::system_clock::time_point timePoint;

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
		// You CANNOT make a part instance without some data and a PUID.
		PartInstance() = delete;

		PartInstance(string ID, timePoint captureTime, cv::Mat img) : 
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
		
		string m_ID;
		string m_PartNumber;
		string m_CategoryNumber;
		string m_CategoryName;
		cv::Mat m_Image;
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

struct ClientConfig
{
	spdlog::level::level_enum m_logLevel;
	string m_clientName;
	string m_assetPath;
	INIReader* m_iniReader;
};

class ClientBase
{
public:
	virtual int Main() = 0;
	void GetParts(std::vector<Parts::PartInstance>& partList);

	ClientBase(ClientConfig config) : 
		m_logLevel(config.m_logLevel), 
		m_clientName(config.m_clientName),
		m_assetPath(config.m_assetPath),
		m_iniReader(config.m_iniReader),
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
	std::vector<Parts::PartInstance> m_OutputBuffer;
};

#endif // !SS_CLASSES_H_11205B5C8C7047CAAA518874BA2C272C