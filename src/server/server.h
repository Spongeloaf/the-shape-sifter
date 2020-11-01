#pragma once

#include <vector>
#include "../common/ss_classes.h"

class Server
{
public:
	Server();

private:
	bool LoadConfig();

	std::vector<Parts::PartInstance> m_ActivePartList;
	string m_assetPath = "C:\\Users\\peter\\Google Drive\\software_dev\\the_shape_sifter";
	string m_configPath =  m_assetPath + "\\settings.ini";
};