// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#ifndef PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48
#define PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48

#include "../common/ss_classes.h"
#include <windows.h>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include "opencv2/opencv.hpp"
#include <random>
#include <time.h>

// sleep time in milliseconds for simulator
constexpr int kSleepMin = 500;
constexpr int kSleepMax = 5000;

// OpenCV colors and fonts
const cv::Scalar kRed{ 0, 0, 255 };
const cv::Scalar kBlue{ 255, 0, 0 };
constexpr int kNumberThickness = 3;
constexpr cv::HersheyFonts kFont = cv::FONT_HERSHEY_SIMPLEX;

// Statuses track where the part is in the frame.
// EnteringView - Coming in from the top, one edge of the rect touching the top of the frame
// InView - Neither top nor bottom of the shae is touching the top or bottom of the frame
// LeavingView - Bottom of rect is touching bottom of frame
enum class ppObjectStatus
{
	Unclassified,
	EnteringView,
	InView,
	LeavingView,
};

struct ppObject
{
	cv::Rect rect;
	unsigned int objectId;
	ppObjectStatus status;
};

using mat = cv::Mat;
using cvContours = std::vector<std::vector<cv::Point>>;
using cvHierarchy = std::vector<cv::Vec4i>;
using ppObjectList = std::vector<ppObject>;
using Rect = cv::Rect;

enum class VideoMode
{
	camera,
	file
};

class PhotoPhile : public ClientBase
{
public:
	PhotoPhile(ClientConfig config);
	int Main();

private:
	mat GetDetectedObjectMask(const mat& image);
	void GetContours(const mat& image, cvContours& contours, cvHierarchy& hierarchy);
	ppObjectList GetRects(const cvContours& contours);
	void DrawRects(const ppObjectList& rects, mat& image);
	unsigned int GetObjectIndexNumber();
	void MapOldRectsToNew(const ppObjectList& oldRects, ppObjectList& newRects);
	ppObjectStatus FindObjectStatus(const Rect& r);
	cv::Point2i GetRectCenter(const Rect& r);
	void GetPartInstanceId(string& s);

	bool m_viewVideo;
	mat m_beltMask;
	string m_clientName;
	string m_videoPath;
	unsigned int m_NextObjectId;	// Never use this directly! Call GetObjectId()!
	VideoMode m_mode;
	ppObjectList m_LastFrameObjectList;

	// openCV Object detection and background subtraction properties.
	// Most of these are set in the constructor while reading from the config file.

	cv::Ptr<cv::BackgroundSubtractorMOG2> m_BgSubtractor;
	float m_FgLearningRate;		// background subtractor learning rate
	float m_MinContourSize;
	mat m_dilateKernel;
	int m_EdgeOfScreenThreshold;
	cv::Size m_VideoRes;
	cv::Size m_halfNativeResolution;		// This cannot be set until we call Main and open a video. Do not use it before that!
	float m_bgSubtractScale;
};

class PhotophileSimulator : public ClientBase
{
public:
	PhotophileSimulator(ClientConfig config) : ClientBase(config) {};
	int Main() override;
};

#endif // !PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48