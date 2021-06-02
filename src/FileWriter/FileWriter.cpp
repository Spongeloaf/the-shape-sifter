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
  while (true)
  {
    std::this_thread::sleep_for(kUpdateInterval);
    std::optional<Parts::PartInstance> part = GetPartFromInputBuffer();
    if (part)
    {
      fs::path file = m_unlabelledParts;
      file /= part->m_PUID;
      file /= ".png";
      cv::imwrite(file.string(), part->m_Image);
    }
  }
}
