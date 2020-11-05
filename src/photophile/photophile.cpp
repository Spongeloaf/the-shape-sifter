// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#include "photophile.h"

using namespace cv;

int Photophile(ClientConfig config, Parts::PartInstance& partBin)
{
	PhotoPhileProperties ppProperties { config };
	VideoCapture cap;
	if (ppProperties.m_mode == VideoMode::camera)
		cap = VideoCapture(0);
	else
		cap = VideoCapture(ppProperties.m_VideoPath);

	// Check if camera opened successfully
	if (!cap.isOpened())
	{
		ppProperties.m_logger->critical("Error opening video stream or file\n\r");
		return -1;
	}
	while (true)
	{
		Mat frame;
		// Capture frame-by-frame
		cap >> frame;

		// If the frame is empty, break immediately
		if (frame.empty())
			break;

		// Display the resulting frame
		imshow("Frame", frame);

		// Press  ESC on keyboard to exit
		char c = (char)waitKey(25);
		if (c == 27)
			break;
	}

	// When everything done, release the video capture object
	cap.release();

	// Closes all the frames
	destroyAllWindows();

	return 0;
}

PhotoPhileProperties::PhotoPhileProperties(ClientConfig config) : ClientBase(config) 
{		
	m_isOk = true;

	string mode = m_iniReader->Get(m_ClientName, "video_mode", "");
	if (mode == "camera")
		m_mode = VideoMode::camera;
	else if (mode == "file")
		m_mode = VideoMode::file;
	else
		m_isOk = false;

	m_viewVideo = m_iniReader->GetBoolean(m_ClientName, "show_video", 0);

	m_VideoPath = m_assetPath + m_iniReader->Get(m_ClientName, "video_file", "");

	string maskFileName = m_iniReader->Get(m_ClientName, "belt_mask", "");
	if (maskFileName == "")
		m_isOk = false;
	else
	{
		m_beltMask = 0; // = m_assetPath + maskFileName;
	}


}

