/*****************************************************************************************************
    This is the fileWriter module for the sorting machine.
    It writes images of parts taken by the camera to the disk.
*****************************************************************************************************/

#include "FileWriter.h"
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>

namespace fs = std::filesystem;

FileWriter::FileWriter(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader)
  : ClientBase(logLevel, clientName, assetPath, iniReader)
{
  m_assetPath = assetPath;
  m_unlabelledParts = m_assetPath;
  std::string path = m_iniReader->Get("brixit", "unlabelledPartsPath", "");
  path.erase(0, 1);
  std::replace(path.begin(), path.end(), '/', '\\');
  m_unlabelledParts.append("\\" + path);
}
int FileWriter::Main()
{
  while (true)
  {
    std::this_thread::sleep_for(kUpdateInterval);
    std::optional<Parts::PartInstance> part = GetPartFromInputBuffer();
    if (part)
    {
      string file = m_unlabelledParts + "\\" + part->m_PUID + ".png";
      cv::imwrite(file, part->m_Image);
    }
  }
}
