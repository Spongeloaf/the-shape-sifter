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
#include <optional>
#include <random>

#define LOCK_GUARD(var) std::lock_guard<std::mutex> ___scope__(var);

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

const string kNamePhotophile = "PhotoPhile";
const string kNamePhotophileSim = "PhotoPhileSim";
const string kNameSUIP = "SUIP";
const string kNameMtMind = "MtMind";
const string kNameClassiFist = "ClassiFist";
const string kNameBeltBuckle = "BeltBuckle";
const string kNameFileWriter = "FileWriter";

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
		Lost
	};

	enum class BBStatus
	{
		waitAckAdd,
		waitAckAssign,
		Added,
		Assigned,
		Sorted,
		Lost
	};

	struct PartInstance
	{
		// The word "part" in the context of this software generally refers to the software object of an individual part
		// being tracked by the sorting machine. To refer to the actual building brick that is being track, we refer to
		// the individuals as "instances" and categorically refer to them as "bricks".
		//
		// Therefore, the member name m_brickPartNumber refers to the part number of that type of brick in the Bricklink
		// database. Whereas the unique identifier for each instance is a PUID: Part Unique Identification Number.
		//
		// The PUID is like a GUID: 12 alpha-numeric characters long, generated at random.

		PartInstance(){};

		// Convenience constructor for the Photophile
		PartInstance(string ID, std::chrono::system_clock::time_point captureTime, cv::Mat img) :
			m_PUID(ID), 
			m_brickPartNumber(""),
			m_brickCategoryNumber(""),
			m_brickCategoryName(""),
			m_Image(img),
			m_BinNumber(0),
			m_CameraOffset(0),
			m_ServerStatus(ServerStatus::newPart),
			m_BBStatus(BBStatus::waitAckAdd),
			m_TimeMTM(),
			m_TimePhile(captureTime),
			m_TimeCF(),
			m_TimeBB(),
			m_TimeBBAssigned()
		{};

		PartInstance(const PartInstance& part) :
			m_PUID (part.m_PUID),
			m_BinNumber(part.m_BinNumber),
			m_CameraOffset(part.m_CameraOffset),
			m_brickPartNumber(part.m_brickPartNumber),
			m_brickCategoryNumber(part.m_brickCategoryNumber),
			m_brickCategoryName(part.m_brickCategoryName),
			m_Image(part.m_Image),
			m_ServerStatus(part.m_ServerStatus),
			m_BBStatus(part.m_BBStatus),
			m_TimeMTM(part.m_TimeMTM),
			m_TimePhile(part.m_TimePhile),
			m_TimeCF(part.m_TimeCF),
			m_TimeBB(part.m_TimeBB),
			m_TimeBBAssigned(part.m_TimeBBAssigned)
		{};

		string m_PUID;
		cv::Mat m_Image;
		unsigned int m_BinNumber;
		int m_CameraOffset;
		ServerStatus m_ServerStatus;
		BBStatus m_BBStatus;
		string m_brickPartNumber;
		string m_brickCategoryNumber;
		string m_brickCategoryName;
		std::chrono::system_clock::time_point m_TimePhile;
		std::chrono::system_clock::time_point m_TimeMTM;
		std::chrono::system_clock::time_point m_TimeCF;
		std::chrono::system_clock::time_point m_TimeBB;
		std::chrono::system_clock::time_point m_TimeBBAssigned;
	};

};	// namespace Parts

using PartList = std::unordered_map<string, Parts::PartInstance>;

class ClientBase
{
public:
	ClientBase(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader) :
		m_logLevel(logLevel), 
		m_clientName(clientName),
		m_assetPath(assetPath),
		m_iniReader(iniReader),
		m_isOk(false)
		{
			// Create basic file logger (not rotated)
			m_logger = spdlog::basic_logger_mt(m_clientName, m_clientName + ".log", true /* delete old logs */);
			m_logger->set_level(spdlog::level::debug);
			m_logger->info(m_clientName + " online");
			m_logger->flush();
		};

	virtual int Main() { return -1; };
	void SendPartsToServer(PartList& partList);
	void SendPartToClient(Parts::PartInstance& part);
	void CopyServerPartListToClient(PartList& partList);

protected:
	std::optional<Parts::PartInstance> GetPartFromInputBuffer();
	void PutPartInOutputBuffer(Parts::PartInstance& part);
	void TimeStampPart(Parts::PartInstance& part);
	unsigned int RandomInteger();

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
	std::mt19937 m_RandomGenerator;
	std::uniform_int_distribution<> m_RandomDistribution;
};

#endif // !SS_CLASSES_H_11205B5C8C7047CAAA518874BA2C272C