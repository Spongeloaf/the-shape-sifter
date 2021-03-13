#include "Classifist.h"

Classifist::Classifist(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader)
		: ClientBase(logLevel, clientName, assetPath, iniReader){};

int Classifist::Main()
{
	// Just a simulator right now!
	while (true)
	{
		std::this_thread::sleep_for(kUpdateInterval);
		std::optional<Parts::PartInstance> part = GetPartFromInputBuffer();
		if (part)
		{
			try
			{
				part->m_BinNumber = std::stoi(part->m_brickCategoryNumber);
			}
			catch (...)
			{
				m_logger->error("Invalid brickCategoryNumber: " + part->m_brickCategoryNumber);
				part->m_BinNumber = 0;
			}
		}
	}

	return 0;
}
