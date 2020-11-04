// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#pragma once

#include "../common/ss_classes.h"

void RunPhotophile(ClientConfig config, Parts::PartInstance& partBin);

enum class VideoMode
{
	camera,
	file
};

class PhotoPhile : ClientBase
{
public:
	PhotoPhile(ClientConfig config);

private:
	Parts::image m_beltMask; // should be converted to cv2 mat, probably.
	VideoMode m_mode;
	bool m_viewVideo;
};
