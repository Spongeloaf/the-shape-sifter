// Mt Mind - A client for the sorting machine that serves as an interface to the neural network that will identify lego
// parts.

#ifndef MTMIND_H
#define MTMIND_H

#include "..\common\ss_classes.h"

class MtMind : public ClientBase
{
public:
	MtMind(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader);
	int Main();
};

#endif  // MTMIND_H