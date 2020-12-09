// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#ifndef PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48
#define PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48

#include "../common/ss_classes.h"
#include <windows.h>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include "opencv2/opencv.hpp"
#include <random>

// sleep time in milliseconds for simulator
constexpr int kSleepMin = 500;
constexpr int kSleepMax = 5000;

int Photophile(ClientConfig config, Parts::PartInstance& partBin);

enum class VideoMode
{
	camera,
	file
};

struct PhotoPhileProperties : ClientBase
{
	PhotoPhileProperties(ClientConfig config);

	Parts::image m_beltMask; // should be converted to cv2 mat, probably.
	VideoMode m_mode;
	bool m_viewVideo;
	string m_VideoPath;

};

#endif // !PHOTOPHILE_H_9EEBDD8A14DB43B992C657E2C80DCD48