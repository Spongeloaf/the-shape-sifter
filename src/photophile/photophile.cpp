// The PhotoPhile is a program that captures pictures of parts on the belt and sends them to the server.

#include "photophile.h"
#include <windows.h>

void RunPhotophile(ClientConfig config, Parts::PartInstance& partBin)
{
	PhotoPhile photoPhile { config };
	int num = 0;

	while (true)
	{
		partBin = Parts::PartInstance(string("ID!"), std::chrono::high_resolution_clock::now(), num);
		num++;
		Sleep(10000);
	}
}

PhotoPhile::PhotoPhile(ClientConfig config) : ClientBase(config) 
{		
	m_isOk = true;

	string mode = m_config.m_iniReader->Get(m_ClientName, "video_mode", "");
	if (mode == "camera")
		m_mode = VideoMode::camera;
	else if (mode == "file")
		m_mode = VideoMode::file;
	else
		m_isOk = false;

	m_viewVideo = m_config.m_iniReader->GetBoolean(m_ClientName, "show_video", 0);

	string maskFileName = m_config.m_iniReader->Get(m_ClientName, "belt_mask", "");
	if (maskFileName == "")
		m_isOk = false;
	else
	{
		m_beltMask = 0; // = m_config.m_assetPath + maskFileName;
	}
}
