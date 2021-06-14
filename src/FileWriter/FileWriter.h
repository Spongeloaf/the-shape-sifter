/*****************************************************************************************************
    This is the fileWriter module for the sorting machine. 
    It writes images of parts taken by the camera to the disk.
*****************************************************************************************************/

#ifndef FILE_WRITER_H_958836bf_49f7_4b25_b871_5060509e9ad9
#define FILE_WRITER_H_958836bf_49f7_4b25_b871_5060509e9ad9

#include "../common/ss_classes.h"
#include  <filesystem>

class FileWriter : public ClientBase
{
public:
  FileWriter(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader);
  int Main();

private:
  string m_assetPath;
  string m_unlabelledParts;
};

#endif // FILE_WRITER_H_958836bf_49f7_4b25_b871_5060509e9ad9