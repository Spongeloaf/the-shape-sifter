#ifndef SUIP_H_FCC8DBC7_86BA_4668_A384_0C26B672F78B
#define SUIP_H_FCC8DBC7_86BA_4668_A384_0C26B672F78B

#include "../common/ss_classes.h"
#include "suipUI.h"

class SUIP : public ClientBase
{
public:
	SUIP(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader);
	int Main();

private:
	Ui_MainWindow UiWindow;
	void SetDarkTheme(QApplication& app);
};


#endif // !SUIP_H_FCC8DBC7_86BA_4668_A384_0C26B672F78B