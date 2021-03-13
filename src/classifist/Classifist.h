// The Classifist is a client that decied which bin parts get sorted into

#ifndef CLASSIFIST_H

#include "../common/ss_classes.h"

class Classifist : public ClientBase
{
public:
	Classifist(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader);
	int Main();
};

#endif  // !CLASSIFIST_H