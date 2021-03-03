// Mt Mind - A client for the sorting machine that serves as an interface to the neural network that will identify lego parts.

#include "mt_mind.h"

constexpr std::chrono::duration<double, std::milli> kSimlulatedDelay(300);

MtMind::MtMind(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader)
		: ClientBase(logLevel, clientName, assetPath, iniReader){};

int MtMind::Main()
{
	// Just a simulator right now!
	while (true)
	{
		std::this_thread::sleep_for(kSimlulatedDelay);
		std::optional<Parts::PartInstance> part = GetPartFromInputBuffer();
		if (part)
		{
		part->m_brickCategoryNumber = "5";
		part->m_brickPartNumber = "2456";
		part->m_brickCategoryName = "SIM CATEGORY";
		PutPartInOutputBuffer(part.value());
		}
	}

	return 0;
}