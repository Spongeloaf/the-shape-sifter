#include "suip.h"

namespace
{
	bool PUIDCompare(const Parts::PartInstance& a, const Parts::PartInstance& b)
	{
		return a.m_TimeMTM < b.m_TimeMTM;
	};

}  // namespace

	int SUIP::Main()
{
	// Setup UI
	int argc = 0;
	char argv[] = "x";
	char* pArgv = argv;
	QApplication app(argc, &pArgv);
	QMainWindow windowBase;
	UIMainWIndow ui;
	ui.setupUi(&windowBase, &app, &m_InputBuffer);
	windowBase.show();
	return app.exec();
}

SUIP::SUIP(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader)
		: ClientBase(logLevel, clientName, assetPath, iniReader){};

void UIMainWIndow::setupUi(QMainWindow* MainWindow, QApplication* app, PartList* partList)
{
	SetupQTLayout(MainWindow);
	SetDarkTheme(app);

	refreshTimer = new QTimer(MainWindow);
	refreshTimer->connect(refreshTimer, &QTimer::timeout, this, &UIMainWIndow::UpdatePartTable);
	refreshTimer->start(kUIUpdateTime);

	m_pPartList = partList;
}

void UIMainWIndow::SetupQTLayout(QMainWindow* MainWindow)
{
	if (MainWindow->objectName().isEmpty())
		MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
	MainWindow->resize(963, 716);
	actionNew_sorting_rules = new QAction(MainWindow);
	actionNew_sorting_rules->setObjectName(QString::fromUtf8("actionNew_sorting_rules"));
	QIcon icon;
	QString iconThemeName = QString::fromUtf8("new");
	if (QIcon::hasThemeIcon(iconThemeName))
	{
		icon = QIcon::fromTheme(iconThemeName);
	}
	else
	{
		icon.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
	}
	actionNew_sorting_rules->setIcon(icon);
	actionLoad_sorting_rules = new QAction(MainWindow);
	actionLoad_sorting_rules->setObjectName(QString::fromUtf8("actionLoad_sorting_rules"));
	actionSave_sorting_rules = new QAction(MainWindow);
	actionSave_sorting_rules->setObjectName(QString::fromUtf8("actionSave_sorting_rules"));
	actionSave_sorting_rules_as = new QAction(MainWindow);
	actionSave_sorting_rules_as->setObjectName(QString::fromUtf8("actionSave_sorting_rules_as"));
	actionShutdown_server_and_exit = new QAction(MainWindow);
	actionShutdown_server_and_exit->setObjectName(QString::fromUtf8("actionShutdown_server_and_exit"));
	actionOpen_log_folder = new QAction(MainWindow);
	actionOpen_log_folder->setObjectName(QString::fromUtf8("actionOpen_log_folder"));
	actionAbout = new QAction(MainWindow);
	actionAbout->setObjectName(QString::fromUtf8("actionAbout"));
	actionHelp = new QAction(MainWindow);
	actionHelp->setObjectName(QString::fromUtf8("actionHelp"));
	actionInsert_menu_items_here = new QAction(MainWindow);
	actionInsert_menu_items_here->setObjectName(QString::fromUtf8("actionInsert_menu_items_here"));
	centralwidget = new QWidget(MainWindow);
	centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
	verticalLayout = new QVBoxLayout(centralwidget);
	verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
	verticalLayout_2 = new QVBoxLayout();
	verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
	tabWidget = new QTabWidget(centralwidget);
	tabWidget->setObjectName(QString::fromUtf8("tabWidget"));
	tab_sorting = new QWidget();
	tab_sorting->setObjectName(QString::fromUtf8("tab_sorting"));
	horizontalLayout_5 = new QHBoxLayout(tab_sorting);
	horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
	verticalLayout_3 = new QVBoxLayout();
	verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
	label_5 = new QLabel(tab_sorting);
	label_5->setObjectName(QString::fromUtf8("label_5"));

	verticalLayout_3->addWidget(label_5);

	table_server_log = new QTableWidget(tab_sorting);
	table_server_log->setObjectName(QString::fromUtf8("table_server_log"));
	QSizePolicy sizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
	sizePolicy.setHorizontalStretch(0);
	sizePolicy.setVerticalStretch(0);
	sizePolicy.setHeightForWidth(table_server_log->sizePolicy().hasHeightForWidth());
	table_server_log->setSizePolicy(sizePolicy);

	verticalLayout_3->addWidget(table_server_log);

	horizontalLayout_5->addLayout(verticalLayout_3);

	tabWidget->addTab(tab_sorting, QString());
	tab_active_parts = new QWidget();
	tab_active_parts->setObjectName(QString::fromUtf8("tab_active_parts"));
	verticalLayout_4 = new QVBoxLayout(tab_active_parts);
	verticalLayout_4->setObjectName(QString::fromUtf8("verticalLayout_4"));
	label_8 = new QLabel(tab_active_parts);
	label_8->setObjectName(QString::fromUtf8("label_8"));

	verticalLayout_4->addWidget(label_8);

	table_active_parts = new QTableWidget(kPartTableRows, kPartTableColumns, tab_active_parts);
	table_active_parts->setHorizontalHeaderLabels(tableHeaders);
	table_active_parts->setObjectName(QString::fromUtf8("table_active_parts"));

	verticalLayout_4->addWidget(table_active_parts);

	tabWidget->addTab(tab_active_parts, QString());

	verticalLayout_2->addWidget(tabWidget);

	verticalLayout->addLayout(verticalLayout_2);

	horizontalLayout_2 = new QHBoxLayout();
	horizontalLayout_2->setSpacing(6);
	horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
	horizontalLayout_2->setSizeConstraint(QLayout::SetMinAndMaxSize);
	verticalLayout_7 = new QVBoxLayout();
	verticalLayout_7->setObjectName(QString::fromUtf8("verticalLayout_7"));
	label_2 = new QLabel(centralwidget);
	label_2->setObjectName(QString::fromUtf8("label_2"));
	label_2->setAlignment(Qt::AlignRight | Qt::AlignTrailing | Qt::AlignVCenter);

	verticalLayout_7->addWidget(label_2);

	label = new QLabel(centralwidget);
	label->setObjectName(QString::fromUtf8("label"));
	label->setAlignment(Qt::AlignRight | Qt::AlignTrailing | Qt::AlignVCenter);

	verticalLayout_7->addWidget(label);

	horizontalLayout_2->addLayout(verticalLayout_7);

	verticalLayout_8 = new QVBoxLayout();
	verticalLayout_8->setObjectName(QString::fromUtf8("verticalLayout_8"));
	label_4 = new QLabel(centralwidget);
	label_4->setObjectName(QString::fromUtf8("label_4"));
	label_4->setPixmap(QPixmap(QString::fromUtf8(":/led/red_led.bmp")));

	verticalLayout_8->addWidget(label_4);

	label_3 = new QLabel(centralwidget);
	label_3->setObjectName(QString::fromUtf8("label_3"));
	label_3->setPixmap(QPixmap(QString::fromUtf8(":/led/red_led.bmp")));

	verticalLayout_8->addWidget(label_3);

	horizontalLayout_2->addLayout(verticalLayout_8);

	horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

	horizontalLayout_2->addItem(horizontalSpacer);

	verticalLayout_5 = new QVBoxLayout();
	verticalLayout_5->setObjectName(QString::fromUtf8("verticalLayout_5"));
	button_start_sorting = new QPushButton(centralwidget);
	button_start_sorting->setObjectName(QString::fromUtf8("button_start_sorting"));
	button_start_sorting->setMinimumSize(QSize(100, 0));

	verticalLayout_5->addWidget(button_start_sorting);

	button_stop_sorting = new QPushButton(centralwidget);
	button_stop_sorting->setObjectName(QString::fromUtf8("button_stop_sorting"));
	button_stop_sorting->setMinimumSize(QSize(100, 0));

	verticalLayout_5->addWidget(button_stop_sorting);

	horizontalLayout_2->addLayout(verticalLayout_5);

	verticalLayout_6 = new QVBoxLayout();
	verticalLayout_6->setObjectName(QString::fromUtf8("verticalLayout_6"));
	button_apply_sorting = new QPushButton(centralwidget);
	button_apply_sorting->setObjectName(QString::fromUtf8("button_apply_sorting"));
	button_apply_sorting->setMinimumSize(QSize(100, 0));

	verticalLayout_6->addWidget(button_apply_sorting);

	butto_load_sorting = new QPushButton(centralwidget);
	butto_load_sorting->setObjectName(QString::fromUtf8("butto_load_sorting"));
	butto_load_sorting->setMinimumSize(QSize(100, 0));

	verticalLayout_6->addWidget(butto_load_sorting);

	horizontalLayout_2->addLayout(verticalLayout_6);

	verticalLayout_9 = new QVBoxLayout();
	verticalLayout_9->setObjectName(QString::fromUtf8("verticalLayout_9"));
	pushButton = new QPushButton(centralwidget);
	pushButton->setObjectName(QString::fromUtf8("pushButton"));
	pushButton->setMinimumSize(QSize(100, 0));

	verticalLayout_9->addWidget(pushButton);

	pushButton_2 = new QPushButton(centralwidget);
	pushButton_2->setObjectName(QString::fromUtf8("pushButton_2"));
	pushButton_2->setMinimumSize(QSize(100, 0));

	verticalLayout_9->addWidget(pushButton_2);

	horizontalLayout_2->addLayout(verticalLayout_9);

	verticalLayout->addLayout(horizontalLayout_2);

	MainWindow->setCentralWidget(centralwidget);
	menubar = new QMenuBar(MainWindow);
	menubar->setObjectName(QString::fromUtf8("menubar"));
	menubar->setGeometry(QRect(0, 0, 963, 20));
	MainWindow->setMenuBar(menubar);
	statusbar = new QStatusBar(MainWindow);
	statusbar->setObjectName(QString::fromUtf8("statusbar"));
	MainWindow->setStatusBar(statusbar);

	retranslateUi(MainWindow);
	tabWidget->setCurrentIndex(0);
	QMetaObject::connectSlotsByName(MainWindow);
}

void UIMainWIndow::retranslateUi(QMainWindow* MainWindow)
{
	MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "MainWindow", nullptr));
	actionNew_sorting_rules->setText(QCoreApplication::translate("MainWindow", "New sorting rules", nullptr));
	actionLoad_sorting_rules->setText(QCoreApplication::translate("MainWindow", "Load sorting rules", nullptr));
	actionSave_sorting_rules->setText(QCoreApplication::translate("MainWindow", "Save sorting rules", nullptr));
	actionSave_sorting_rules_as->setText(QCoreApplication::translate("MainWindow", "Save sorting rules as....", nullptr));
	actionShutdown_server_and_exit->setText(
			QCoreApplication::translate("MainWindow", "Shutdown server and exit", nullptr));
	actionOpen_log_folder->setText(QCoreApplication::translate("MainWindow", "Open log folder", nullptr));
	actionAbout->setText(QCoreApplication::translate("MainWindow", "About", nullptr));
	actionHelp->setText(QCoreApplication::translate("MainWindow", "Help", nullptr));
	actionInsert_menu_items_here->setText(QCoreApplication::translate("MainWindow", "nothing here yet", nullptr));
	label_5->setText(QCoreApplication::translate("MainWindow", "Server Log", nullptr));
	tabWidget->setTabText(tabWidget->indexOf(tab_sorting), QCoreApplication::translate("MainWindow", "Logs", nullptr));
	label_8->setText(QCoreApplication::translate("MainWindow", "Active Part Table", nullptr));
	tabWidget->setTabText(tabWidget->indexOf(tab_active_parts),
												QCoreApplication::translate("MainWindow", "Active Parts", nullptr));
	label_2->setText(QCoreApplication::translate("MainWindow", "Server Status:", nullptr));
	label->setText(QCoreApplication::translate("MainWindow", "Belt Buckle Status:", nullptr));
	label_4->setText(QString());
	label_3->setText(QString());
	button_start_sorting->setText(QCoreApplication::translate("MainWindow", "Start Sorting", nullptr));
	button_stop_sorting->setText(QCoreApplication::translate("MainWindow", "Stop Sorting", nullptr));
	button_apply_sorting->setText(QCoreApplication::translate("MainWindow", "Start Belt", nullptr));
	butto_load_sorting->setText(QCoreApplication::translate("MainWindow", "Stop Belt", nullptr));
	pushButton->setText(QCoreApplication::translate("MainWindow", "Clear Active Parts", nullptr));
	pushButton_2->setText(QCoreApplication::translate("MainWindow", "Calibrate Bins", nullptr));
}

void UIMainWIndow::UpdatePartTable()
{
	if (!m_pPartList)
		return;

	table_active_parts->clearContents();

	std::vector<Parts::PartInstance> SortedPartsList;
	SortedPartsList.reserve(m_pPartList->size());
	for (const auto& [key, value] : *m_pPartList)
	{
		SortedPartsList.push_back(value);
	}

	std::sort(SortedPartsList.begin(), SortedPartsList.end(), &PUIDCompare);

	int i = 0;
	for (auto& part : SortedPartsList)
	{
		QStringList strList = CreateQStringListFromPart(part);
		for (int j = 0; j < strList.length(); j++)
		{
			QTableWidgetItem* newItem = new QTableWidgetItem(strList[j]);
			table_active_parts->setItem(i, j, newItem);
		}
		i++;
	}
}

void UIMainWIndow::SetDarkTheme(QApplication* app)
{
	app->setStyle("Fusion");

	QPalette dark_palette;
	dark_palette.setColor(QPalette::Window, QColor(53, 53, 53));
	dark_palette.setColor(QPalette::WindowText, QColor("white"));
	dark_palette.setColor(QPalette::Base, QColor(25, 25, 25));
	dark_palette.setColor(QPalette::AlternateBase, QColor(53, 53, 53));
	dark_palette.setColor(QPalette::ToolTipBase, QColor("white"));
	dark_palette.setColor(QPalette::ToolTipText, QColor("white"));
	dark_palette.setColor(QPalette::Text, QColor("white"));
	dark_palette.setColor(QPalette::Button, QColor(53, 53, 53));
	dark_palette.setColor(QPalette::ButtonText, QColor("white"));
	dark_palette.setColor(QPalette::BrightText, QColor("red"));
	dark_palette.setColor(QPalette::Highlight, QColor(42, 130, 218));
	dark_palette.setColor(QPalette::HighlightedText, QColor("black"));

	app->setPalette(dark_palette);
	app->setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }");
}

inline QString UIMainWIndow::EnumToQStr(Parts::ServerStatus enumm)
{
	using namespace Parts;
	switch (enumm)
	{
		case ServerStatus::newPart:
			return "newPart";

		case ServerStatus::waitMTM:
			return "waitMTM";

		case ServerStatus::MTMDone:
			return "MTMDone";

		case ServerStatus::waitCF:
			return "waitCF";

		case ServerStatus::cfDone:
			return "cfDone";

		case ServerStatus::waitSort:
			return "waitSort";

		case ServerStatus::sortDone:
			return "sortDone";

		case ServerStatus::Lost:
			return "Lost";
	}
}

inline QString UIMainWIndow::EnumToQStr(Parts::BBStatus enumm)
{
	using namespace Parts;
	switch (enumm)
	{
		case BBStatus::waitAckAdd:
			return "waitAckAdd";

		case BBStatus::waitAckAssign:
			return "waitAckAssign";

		case BBStatus::Added:
			return "Added";

		case BBStatus::Assigned:
			return "Assigned";

		case BBStatus::Sorted:
			return "Sorted";

		case BBStatus::Lost:
			return "Lost";
	}
}

inline QStringList UIMainWIndow::CreateQStringListFromPart(Parts::PartInstance& part)
{
	QString ID = QString::fromUtf8(part.m_PUID.c_str());

	QString bin;
	bin.setNum(part.m_BinNumber);

	QString camOffset;
	camOffset.setNum(part.m_CameraOffset);

	QString serverStatus = EnumToQStr(part.m_ServerStatus);
	QString partStatus = EnumToQStr(part.m_BBStatus);
	QString brickPartNumber = QString::fromStdString(part.m_brickPartNumber);
	QString brickCategoryNumber = QString::fromStdString(part.m_brickCategoryNumber);
	QString brickCategoryName = QString::fromStdString(part.m_brickCategoryName);

	QString TimeMTM = QString::fromStdString(date::format("%T", part.m_TimeMTM));
	QString TimePhile = QString::fromStdString(date::format("%T", part.m_TimePhile));
	QString TimeCF = QString::fromStdString(date::format("%T", part.m_TimeCF));
	QString TimeBB = QString::fromStdString(date::format("%T", part.m_TimeBB));
	QString TimeUnused = QString::fromStdString(date::format("%T", part.m_TimeBBAssigned));

	return {ID,
					bin,
					camOffset,
					serverStatus,
					partStatus,
					brickPartNumber,
					brickCategoryNumber,
					brickCategoryName,
					TimePhile,
					TimeMTM,
					TimeCF,
					TimeBB,
					TimeUnused};
}
