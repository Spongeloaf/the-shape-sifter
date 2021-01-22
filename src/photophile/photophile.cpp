// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.
// shroud - An image taken from the camrea which is processed for part detection.

#include "photophile.h"

const cv::Scalar kRed{ 0, 0, 255 };
const cv::Scalar kBlue{ 255, 0, 0 };
constexpr int kNumberThickness = 3;

PhotoPhile::PhotoPhile(ClientConfig config) : ClientBase(config)
{
	m_isOk = true;
	m_clientName = config.m_clientName;

	string mode = m_iniReader->Get(m_clientName, "video_mode", "");
	if (mode == "camera")
		m_mode = VideoMode::camera;
	else if (mode == "file")
		m_mode = VideoMode::file;
	else
		m_isOk = false;

	m_viewVideo = m_iniReader->GetBoolean(m_clientName, "show_video", 0);
	m_videoPath = m_assetPath + m_iniReader->Get(m_clientName, "video_file", "");

	string maskFileName = m_iniReader->Get(m_clientName, "belt_mask", "");
	if (maskFileName == "")
		m_isOk = false;
	else
	{
		maskFileName = m_assetPath + maskFileName;
	}

	m_NextObjectId = 0;
	m_BgSubtractor = cv::createBackgroundSubtractorMOG2();
	m_MinContourSize = m_iniReader->GetFloat(m_clientName, "MinContourSize", 2000.0);
	m_FgLearningRate = m_iniReader->GetFloat(m_clientName, "FgLearningRate", 0.002);
	m_EdgeOfScreenThreshold = m_iniReader->GetInteger(m_clientName, "EdgeOfScreenThreshold", 20);

	m_Font = cv::FONT_HERSHEY_SIMPLEX;

	int kernelX = m_iniReader->GetInteger(m_clientName, "dilateKernelX", 4);
	int kernelY = m_iniReader->GetInteger(m_clientName, "dilateKernelY", 7);
	m_dilateKernel = cv::getStructuringElement(cv::MorphShapes::MORPH_RECT, cv::Size(kernelX, kernelY));
	
	// Edge mask for conveyor belt. Used to eliminate detection of the belt edges.
	m_beltMask = cv::imread(maskFileName, cv::IMREAD_GRAYSCALE);
	cv::threshold(m_beltMask, m_beltMask, 127, 255, cv::THRESH_BINARY);
}

int PhotoPhile::Main()
{
	cv::VideoCapture cap;
	if (m_mode == VideoMode::camera)
		cap = cv::VideoCapture(0);
	else
		cap = cv::VideoCapture(m_videoPath);

	// Check if camera opened successfully
	if (!cap.isOpened())
	{
		m_logger->critical("Error opening video stream or file\n\r");
		return -1;
	}

	m_videoRect = Rect(0, 0, cap.get(cv::CAP_PROP_FRAME_WIDTH), cap.get(cv::CAP_PROP_FRAME_HEIGHT));

	while (true)
	{
		auto start = std::chrono::system_clock::now();

		mat image;
		// Capture frame-by-frame
		cap >> image;

		// If the frame is empty, break immediately
		if (image.empty())
			continue;

		// We need to preserve the original frame
		mat shroud = GetDetectedObjectMask(image);

		cvContours conts;
		cvHierarchy hier;
		GetContours(shroud, conts, hier);

		ppObjectList rects = GetRects(conts);

		MapOldRectsToNew();

		DrawRects(rects, image);

		m_LastFrameObjectList = rects;
		auto end = std::chrono::system_clock::now();
		string elapsed = std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count());

		// Process time
		cv::putText(image, "Parts: " + std::to_string(rects.size()), cv::Point(20, 650), m_Font, 1, kRed, 2);
		cv::putText(image, "Time:  " + elapsed, cv::Point(10, 700), m_Font, 1, kRed, 2);

		// Display the resulting frame
		cv::imshow("Frame Raw", image);

		// Display the resulting frame
		cv::imshow("Frame Shroud", shroud);

		// Press  ESC on keyboard to exit
		char c = (char)cv::waitKey(1);
		if (c == 27)
			break;
	}

	// When everything done, release the video capture object
	cap.release();

	// Closes all the frames
	cv::destroyAllWindows();

	return 0;
}

/****************************************
Name:	PhotoPhile::GetDetectedObjectMask
Action:	Use the background subtractor to create black/white mask of any shapes in the image.
****************************************/
mat PhotoPhile::GetDetectedObjectMask(const mat& image)
{
	mat shroud = image.clone();
	cv::dilate(shroud, shroud, m_dilateKernel);

	// Background subtraction requires a grayscale image.
	// Does it really need to be grayscale?
	cv::cvtColor(shroud, shroud, cv::COLOR_BGR2GRAY);

	// blur the image to remove noise
	cv::blur(shroud, shroud, cv::Size(7, 7));
	m_BgSubtractor->apply(shroud, shroud, m_FgLearningRate);
	cv::bitwise_and(shroud, m_beltMask, shroud);
	return shroud;
}

/****************************************
Name:	PhotoPhile::GetContours
Action:	Get contours from the image and drop any that are too small.
****************************************/
void PhotoPhile::GetContours(const mat& image, cvContours& OutConts, cvHierarchy& hierarchy)
{
	cvContours workingConts;
	cv::findContours(image, workingConts, hierarchy, cv::RetrievalModes::RETR_EXTERNAL, cv::ContourApproximationModes::CHAIN_APPROX_SIMPLE);
	for (auto c : workingConts)
	{
		if (cv::contourArea(c) > m_MinContourSize)
		{
			OutConts.push_back(c);
		}
	}
}

/********************************************************************************
Name:	PhotoPhile::GetRects
Action:	Creates a PhotoPhile Object list from the contours. Includes bounding boxes and object ID numbers
********************************************************************************/
ppObjectList PhotoPhile::GetRects(const cvContours& contours)
{
	ppObjectList list;
	for (auto c : contours)
	{
		Rect r = cv::boundingRect(c);
		ppObject o{ r, GetObjectId(), FindObjectStatus(r) };
		list.push_back(o);
	}

	auto lowestY = [this](const ppObject& a, const ppObject& b) { return GetRectCenter(a.rect).y < GetRectCenter(b.rect).y; };
	std::sort(list.begin(), list.end(), lowestY);
	
	return list;
}

/********************************************************************************
Name:	PhotoPhile::DrawRects
Action:	Draws bounding boxes on the frame along with their object ID numbers
********************************************************************************/
void PhotoPhile::DrawRects(const ppObjectList& objects, mat& image)
{
	for (const ppObject& o : objects)
	{
		cv::rectangle(image, o.rect, kRed);
		cv::Point2f center = (o.rect.br() + o.rect.tl()) * 0.5;
		cv::putText(image, std::to_string(o.objectId), center, m_Font, 1.0, kRed, kNumberThickness);
	}
}

unsigned int PhotoPhile::GetObjectId()
{
	return m_NextObjectId++;
}

void PhotoPhile::MapOldRectsToNew(const ppObjectList& oldRects, ppObjectList& newRects)
{
	// loop through new rects
	// Remove rects that are LeavingView.

	// Any rect that is InView and used to be EnteringView should be dispatched to server
	// Count number of EnteringView from last frame and EnteringView from this frame.
	// If fewer EnteringView this frame, we must need to add a new part.
	// Find the closest match to the part(s)  that are no longer EnteringView by distance to center.
	
	int newEntering = 0;
	int oldEntering = 0;

	// Count how many objects are entering the frame
	auto newIt = newRects.begin();
	while (newIt != newRects.end())
	{
		if (newIt->status == ppObjectStatus::EnteringView)
			newEntering++;

		if (newIt->status == ppObjectStatus::LeavingView)
		{
			newIt = newRects.erase(newIt);
		}
	}

	// Count how many we are already aware of
	auto oldIt = oldRects.begin();
	for (auto& old : oldRects)
	{
		if (old.status == ppObjectStatus::EnteringView)
			oldEntering++;
	}

	// For each newly entered object, dispatch a part to the server and track it.
	if (newEntering < oldEntering)
	{
		// Match up those parts baby!
		// There must be at least one part to match up!
		int matches = oldEntering - newEntering;
		for (int i = 0; i < matches; i++)
		{

		}
	}
}

cv::Point2i PhotoPhile::GetRectCenter(const Rect& r)
{
	return (r.br() + r.tl()) * 0.5;
}

int PhotophileSimulator(ClientConfig config, Parts::PartInstance& partBin)
{
	PhotoPhile ppProperties( config );

	std::random_device rd;     // only used once to initialise (seed) engine
	std::mt19937 rng(rd());    // random-number engine used (Mersenne-Twister in this case)
	std::uniform_int_distribution<int> sleepTimer(kSleepMin, kSleepMax);

	while (true)
	{
		std::cout << "Good Morning!\n\r";

		auto random_integer = sleepTimer(rng);
		std::chrono::duration<int, std::milli> tSleep(random_integer);
		std::this_thread::sleep_for(tSleep);
	}
}
