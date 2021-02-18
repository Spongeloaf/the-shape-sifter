#include "suipClient.h"

SUIP::SUIP(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader) : ClientBase(logLevel, clientName, assetPath, iniReader)
{}

int SUIP::Main()
{
	int argc = 0;
	char argv[] = "x";
	char* pArgv = argv;
	QApplication app(argc, &pArgv);
	SetDarkTheme(app);
	QMainWindow windowBase;
	UiWindow.setupUi(&windowBase, &app, &m_InputBuffer);
	windowBase.show();

	return app.exec();
}

void SUIP::CopyPartsListFromServer(PartList& partList)
{
	m_InputBuffer = partList;
}

void SUIP::SetDarkTheme(QApplication& app)
{
	app.setStyle("Fusion");

	QPalette dark_palette;
	dark_palette.setColor(QPalette::Window, QColor(53, 53, 53));
	dark_palette.setColor(QPalette::WindowText, QColorConstants::White);
	dark_palette.setColor(QPalette::Base, QColor(25, 25, 25));
	dark_palette.setColor(QPalette::AlternateBase, QColor(53, 53, 53));
	dark_palette.setColor(QPalette::ToolTipBase, QColorConstants::White);
	dark_palette.setColor(QPalette::ToolTipText, QColorConstants::White);
	dark_palette.setColor(QPalette::Text, QColorConstants::White);
	dark_palette.setColor(QPalette::Button, QColor(53, 53, 53));
	dark_palette.setColor(QPalette::ButtonText, QColorConstants::White);
	dark_palette.setColor(QPalette::BrightText, QColorConstants::Red);
	dark_palette.setColor(QPalette::Highlight, QColor(42, 130, 218));
	dark_palette.setColor(QPalette::HighlightedText, QColorConstants::Black);

	app.setPalette(dark_palette);
	app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }");
}
