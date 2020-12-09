// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#ifndef PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48
#define PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48

#include "../common/ss_classes.h"
#include <windows.h>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include "opencv2/opencv.hpp"
#include <random>

using Mat = cv::Mat;

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
	string m_ClientName;
	Mat m_BeltMask;
	VideoMode m_mode;
	bool m_viewVideo;
	string m_VideoPath;

	// openCV Object detection and background subtraction properties.
	int m_MinContourSize;
	cv::Ptr<cv::BackgroundSubtractorMOG2> m_BgSubtractor;
	Mat m_dilateKernel;
	cv::HersheyFonts m_Font;
	double m_FgLearningRate;		// background subtractor learning rate
};

#endif // !PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48