// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#ifndef PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48
#define PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48

#include "../common/ss_classes.h"
#include <windows.h>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include "opencv2/opencv.hpp"
#include <random>

using mat = cv::Mat;
using cvContours = std::vector<std::vector<cv::Point>>;
using cvHierarchy = std::vector<cv::Vec4i>;
using ppObjectList = std::vector<cv::Rect>;
using rect = cv::Rect;

// sleep time in milliseconds for simulator
constexpr int kSleepMin = 500;
constexpr int kSleepMax = 5000;

enum class VideoMode
{
	camera,
	file
};

class PhotoPhile : ClientBase
{
public:
	PhotoPhile(ClientConfig config);
	int Main();

private:
	mat GetDetectedObjectMask(const mat& image);
	void GetContours(const mat& image, cvContours& contours, cvHierarchy& hierarchy);
	ppObjectList GetRects(const cvContours& contours);
	void DrawRects(const ppObjectList& rects, mat& image);

	string m_clientName;
	mat m_beltMask;
	VideoMode m_mode;
	bool m_viewVideo;
	string m_videoPath;
	rect m_videoRect;	// This cannot be set until we call Main and open a video. Do not use it before that!

	// openCV Object detection and background subtraction properties.
	double m_MinContourSize;
	cv::Ptr<cv::BackgroundSubtractorMOG2> m_BgSubtractor;
	mat m_dilateKernel;
	cv::HersheyFonts m_Font;
	double m_FgLearningRate;		// background subtractor learning rate
};

#endif // !PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48