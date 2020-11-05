// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#pragma once

#include "../common/ss_classes.h"
#include <windows.h>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include "opencv2/opencv.hpp"

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
