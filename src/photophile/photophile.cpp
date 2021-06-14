// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.
// shroud - An image taken from the camrea which is processed for part detection.

#include "photophile.h"

namespace
{
	cv::Point2i GetRectCenter(const Rect& r)
	{
		return (r.br() + r.tl()) * 0.5;
	}

	bool lowestY(const ppObject& a, const ppObject& b)
	{
		return GetRectCenter(a.rect).y < GetRectCenter(b.rect).y;
	}

};	//namespace

PhotoPhile::PhotoPhile(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader) : ClientBase(logLevel, clientName, assetPath, iniReader)
{
	m_isOk = true;
	m_clientName = clientName;

	string mode = m_iniReader->Get(m_clientName, "video_mode", "");
	if (mode == "camera")
		m_mode = VideoMode::camera;
	else if (mode == "file")
		m_mode = VideoMode::file;
	else if (mode == "ip")
		m_mode = VideoMode::ip;
	else
		m_isOk = false;

	m_viewVideo = m_iniReader->GetBoolean(m_clientName, "show_video", 0);
	m_videoPath = m_assetPath + m_iniReader->Get(m_clientName, "video_file", "");

	m_bgSubtractScale = m_iniReader->GetFloat(m_clientName, "BGSubtractScale", 0.5);
	m_BgSubtractor = cv::createBackgroundSubtractorMOG2();
	m_MinContourSize = m_iniReader->GetFloat(m_clientName, "MinContourSize", 2000.0) * m_bgSubtractScale;
	m_FgLearningRate = m_iniReader->GetFloat(m_clientName, "FgLearningRate", 0.002f);
	m_rectanglePadding = m_iniReader->GetInteger(m_clientName, "rectanglePadding", 20);

	int kernelX = m_iniReader->GetInteger(m_clientName, "dilateKernelX", 4);
	int kernelY = m_iniReader->GetInteger(m_clientName, "dilateKernelY", 7);
	m_dilateKernel = cv::getStructuringElement(cv::MorphShapes::MORPH_RECT, cv::Size(kernelX, kernelY));
	
	m_maskFileName = m_iniReader->Get(m_clientName, "belt_mask", "");
	if (m_maskFileName == "")
		m_isOk = false;
	else
		m_maskFileName = m_assetPath + "\\" + m_maskFileName;

	m_cameraNum = m_iniReader->GetInteger(m_clientName, "cameraNum", 0);
	m_IPcameraAddress = m_iniReader->Get(m_clientName, "cameraIP", "");
}

int PhotoPhile::Main()
{
	//cv::VideoCapture cap;
	//if (m_mode == VideoMode::camera)
	//	cap = cv::VideoCapture(m_cameraNum);
	//else if (m_mode == VideoMode::ip)
	//	cap = cv::VideoCapture(m_IPcameraAddress);
	//else
	//	cap = cv::VideoCapture(m_videoPath);

	cv::VideoCapture cap = cv::VideoCapture(m_cameraNum);

	// Check if camera opened successfully
	if (!cap.isOpened())
	{
		m_logger->critical("Error opening video stream or file\n\r");
		return -1;
	}
	
	//auto zz = cv::VideoWriter::fourcc('M', 'J', 'P', 'G'); // 1196444237
	int zz = cap.get(cv::CAP_PROP_MODE);

	bool result = false;

	if (m_mode == VideoMode::camera)
	{
		//result = cap.set(cv::CAP_PROP_FRAME_COUNT, 30);
		result = cap.set(cv::CAP_PROP_FRAME_WIDTH, 1280);
		result = cap.set(cv::CAP_PROP_FRAME_HEIGHT, 720);
		result = cap.set(cv::CAP_PROP_MODE, cv::VideoWriter::fourcc('M', 'J', 'P', 'G'));
		//cap.set(cv::CAP_PROP_EXPOSURE, -9);
		//cap.set(cv::CAP_PROP_WB_TEMPERATURE, 3400);
		//cap.set(cv::CAP_PROP_BRIGHTNESS, 128);
		//cap.set(cv::CAP_PROP_CONTRAST, 128);
		//cap.set(cv::CAP_PROP_SATURATION, 128);
		//cap.set(cv::CAP_PROP_SHARPNESS, 128);
		//cap.set(cv::CAP_PROP_FOCUS, 35);
	}

	int zzz = cap.get(cv::CAP_PROP_MODE);

	m_VideoRes.height = int(cap.get(cv::CAP_PROP_FRAME_HEIGHT));
	m_VideoRes.width = int(cap.get(cv::CAP_PROP_FRAME_WIDTH));
	m_halfNativeResolution.height = int(float(cap.get(cv::CAP_PROP_FRAME_HEIGHT)) * m_bgSubtractScale);
	m_halfNativeResolution.width = int(float(cap.get(cv::CAP_PROP_FRAME_WIDTH)) * m_bgSubtractScale);
	m_NextObjectId = 0;
	m_partCount = 0;

	// Edge mask for conveyor belt. Used to eliminate detection of the belt edges.
	cv::Size maskSize = m_VideoRes;
	maskSize.height = int(float(maskSize.height) * m_bgSubtractScale);
	maskSize.width = int(float(maskSize.width) * m_bgSubtractScale);

	m_beltMask = cv::imread(m_maskFileName, cv::IMREAD_GRAYSCALE);
	cv::resize(m_beltMask, m_beltMask, maskSize, cv::InterpolationFlags::INTER_NEAREST);
	cv::threshold(m_beltMask, m_beltMask, 127, 255, cv::THRESH_BINARY);

	m_RandomGenerator = std::mt19937(std::random_device()());
	std::uniform_int_distribution<> m_RandomDistribution(0, 255);

	bool ready = false;

	while (true)
	{
		auto start = std::chrono::system_clock::now();

		// Capture frame-by-frame
		// cap >> m_CurrentFrame;
		ready = cap.read(m_CurrentFrame);

		// If the frame is empty, break immediately
		if (!ready)
		{
			m_logger->debug("continue");
			continue;
		}

		auto p1 = std::chrono::system_clock::now();
		string p1s = std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(p1 - start).count());

		// We need to preserve the original frame
		mat shroud = GetDetectedObjectMask(m_CurrentFrame);

		cvContours conts;
		cvHierarchy hier;
		GetContours(shroud, conts, hier);

		auto p2 = std::chrono::system_clock::now();
		string p2s = std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(p2 - start).count());

		m_ThisFrameObjectList = GetRects(conts);

		MapOldRectsToNew();

		auto p3 = std::chrono::system_clock::now();
		string p3s = std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(p3 - start).count());

		DrawRects(m_CurrentFrame);

		m_LastFrameObjectList = m_ThisFrameObjectList;

		auto end = std::chrono::system_clock::now();
		string elapsed = std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count());

		// Process time
		cv::putText(m_CurrentFrame, "Parts: " + std::to_string(m_partCount), cv::Point(20, 650), kFont, 1, kRed, 2);
		cv::putText(m_CurrentFrame, "Time:  " + elapsed, cv::Point(10, 700), kFont, 1, kRed, 2);

		// Display the resulting frame
		cv::imshow("Frame Raw", m_CurrentFrame);

		// Display the resulting frame
		cv::imshow("Frame Shroud", shroud);

		// Press  ESC on keyboard to exit
		char c = (char)cv::waitKey(1);
		if (c == 27)
			break;

		string frameProcessInfo = "p1 :" + p1s + ", p2 :" + p2s + ", p3 :" + p3s + ", el :" + elapsed;
		m_logger->debug(frameProcessInfo);
		//if (!rects.empty())
		//{
		//	if ((rects.front().objectId % 10) == 0)
		//	{
		//	Parts::PartInstance p = { GeneratePUID(kPUIDLength), std::chrono::system_clock::now(), mat() };
		//	m_OutputLock.lock();
		//	m_OutputBuffer.push_back(std::move(p));
		//	m_OutputLock.unlock();
		//	}
		//}
	}
	// When everything done, release the video capture object
	cap.release();

	// Closes all the frames
	cv::destroyAllWindows();

	return 0;
}

	/***************************************************************
GeneratePUID()

Creates a Part Unique IDentifier, which is a string of N length ASCII characters.
***************************************************************/
std::string PhotoPhile::GeneratePUID()
{
	std::stringstream ss;

	for (unsigned int i = 0; i < kPUIDLength; i++)
	{
		const auto rc = RandomInteger();
		std::stringstream hexstream;
		hexstream << std::hex << rc;
		auto hex = hexstream.str();
		if (hex.length() < 2)
			ss << hex.at(0);
		else
			ss << hex.at(1);
	}
	return ss.str();
}

/***************************************************************
Name:	PhotoPhile::GetDetectedObjectMask
Action:	Use the background subtractor to create black/white mask of any shapes in the image.
***************************************************************/
mat PhotoPhile::GetDetectedObjectMask(const mat& image)
{
	mat shroud;
	cv::resize(image, shroud, m_halfNativeResolution);

	 //Background subtraction requires a grayscale image.
	 //Does it really need to be grayscale?
	cv::cvtColor(shroud, shroud, cv::COLOR_BGR2GRAY);

	// blur the image to remove noise
	cv::blur(shroud, shroud, cv::Size(7, 7));
	m_BgSubtractor->apply(shroud, shroud, m_FgLearningRate);
	cv::bitwise_and(shroud, m_beltMask, shroud);
	cv::dilate(shroud, shroud, m_dilateKernel);
	return shroud;
}

/***************************************************************
Name:	PhotoPhile::GetContours
Action:	Get contours from the image and drop any that are too small.
***************************************************************/
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

		// The BG Subtractor works on scaled images for performance reasons. We need to scale these rects back up to their original size.
		r.x = int(float(r.x) / m_bgSubtractScale);
		r.y = int(float(r.y) / m_bgSubtractScale);
		r.width = int(float(r.width) / m_bgSubtractScale);
		r.height = int(float(r.height) / m_bgSubtractScale);

		if (IsObjectTouchingEdgeOfFrame(r))
			continue;

		list.push_back({ r, GetObjectIndexNumber() });
	}

	std::sort(list.begin(), list.end(), &lowestY);
	
	return list;
}

/********************************************************************************
Name:	PhotoPhile::DrawRects
Action:	Draws bounding boxes on the frame along with their object ID numbers
********************************************************************************/
void PhotoPhile::DrawRects(mat& image)
{
	for (const ppObject& o : m_ThisFrameObjectList)
	{
		cv::rectangle(image, o.rect, kRed);
		cv::Point2f center = (o.rect.br() + o.rect.tl()) * 0.5;
		cv::putText(image, std::to_string(o.objectId), center, kFont, 1.0, kRed, kNumberThickness);
	}
}

unsigned int PhotoPhile::GetObjectIndexNumber()
{
	return m_NextObjectId++;
}

void PhotoPhile::MapOldRectsToNew()
{
	// loop through new rects
	// Remove rects that are LeavingView.

	// Any rect that is InView and used to be EnteringView should be dispatched to server
	// Count number of EnteringView from last frame and EnteringView from this frame.
	// If fewer EnteringView this frame, we must need to add a new part.
	// Find the closest match to the part(s)  that are no longer EnteringView by distance to center.
	
	if (m_ThisFrameObjectList.size() == 0)
		return;

	for (auto& obj : m_ThisFrameObjectList)
	{
		if (MatchNewRectToOldRect(obj))
			continue;

		obj.objectId = m_partCount;
		DispatchPart(obj);
	}
}

// Returns True if the top or bottom edge of the rect is touching ther top or bottom edge of the frame.
bool PhotoPhile::IsObjectTouchingEdgeOfFrame(const Rect& rect)
{
	if (rect.tl().y < m_rectanglePadding)
		return true;

	if (rect.br().y > (m_VideoRes.height - m_rectanglePadding))
		return true;

	return false;
}

// This could be rolled into the main photophile class as an alternative main loop which could be toggled on by the config file. 
// I suppose I'll get around to it when I need it.
//int PhotophileSimulator::Main()
//{
//	std::random_device rd;     // only used once to initialise (seed) engine
//	std::mt19937 rng(rd());    // random-number engine used (Mersenne-Twister in this case)
//	std::uniform_int_distribution<int> sleepTimer(kSleepMin, kSleepMax);
//
//	while (true)
//	{
//		auto random_integer = sleepTimer(rng);
//		//std::chrono::duration<int, std::milli> tSleep(random_integer);
//		std::chrono::duration<int, std::milli> tSleep(1000);
//		std::this_thread::sleep_for(tSleep);
//
//		Parts::PartInstance p = { GeneratePUID(), std::chrono::system_clock::now(), mat() };
//		m_OutputLock.lock();
//		m_OutputBuffer.insert(std::make_pair(p.m_PUID, std::move(p)));
//		m_OutputLock.unlock();
//	}
//}

bool 	PhotoPhile::MatchNewRectToOldRect(ppObject& r)
{
	// Return true if a matching rect was found. Delete the matched rect from the old list.
	// This list is kept sorted by lowest Y value, and objects are deleted as they are matched. Therefore we can assume that the first item is the best candidate for matching.
	for (auto iter = m_LastFrameObjectList.begin(); iter != m_LastFrameObjectList.end(); iter++)
	{
		// The padding ensures that objects don't get missed from one frame to the next. Sometimes the bbox fluctuate between frames.
		int lastY = GetRectCenter(iter->rect).y - m_rectanglePadding;
		int thisY = GetRectCenter(r.rect).y;
		if (lastY <= thisY)
		{
			// We have a match!
			r.objectId = iter->objectId;
			m_LastFrameObjectList.erase(iter);
			return true;
		}
	}
	return false;
}

void PhotoPhile::DispatchPart(const ppObject& part)
{
	cv::Mat partImg(part.rect.width, part.rect.height, m_CurrentFrame.type());
	m_CurrentFrame(part.rect).copyTo(partImg);
	std::chrono::system_clock::time_point now = std::chrono::system_clock::now();
	Parts::PartInstance newPart(GeneratePUID(), now, partImg);
	
	std::cout << "Part dispatched!\n\r";
	m_partCount++;

	m_OutputLock.lock();
	m_OutputBuffer.insert(std::make_pair(newPart.m_PUID, std::move(newPart)));
	m_OutputLock.unlock();
}