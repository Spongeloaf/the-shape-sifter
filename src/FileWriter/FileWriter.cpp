/*****************************************************************************************************
    This is the fileWriter module for the sorting machine.
    It writes images of parts taken by the camera to the disk.
*****************************************************************************************************/

#include "FileWriter.h"
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>

namespace fs = std::filesystem;

FileWriter::FileWriter(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader)
  : ClientBase(logLevel, clientName, assetPath, iniReader),
  m_assetPath(assetPath)
{
  m_unlabelledParts = m_assetPath;
  m_unlabelledParts /= m_iniReader->Get("brixit", "unlabelledPartsPath", "/images/unlabelledParts");
}
int FileWriter::Main()
{
	return 0;
}