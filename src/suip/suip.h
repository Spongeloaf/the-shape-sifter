/********************************************************************************
** Form generated from reading UI file 'suip.ui'
**
** Created by: Qt User Interface Compiler version 6.0.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef SUIP_H
#define SUIP_H

#define _SILENCE_ALL_CXX17_DEPRECATION_WARNINGS

#include "..\common\ss_classes.h"

#include <date\date.h>
#include <Qtcore/qobject.h>
#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QTableWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>
#include <QtCore/QTimer>

class SUIP : public ClientBase
{
public:
	// The SUIP will use the QT even loop instead of a client Main(). It does not get threaded like a regular
	// client, we just inherited from it to get logging and other common functionality
	int Main();
	SUIP(spdlog::level::level_enum logLevel, string clientName, string assetPath, INIReader* iniReader);
};

QT_BEGIN_NAMESPACE

class UIMainWIndow : public QObject
{
	Q_OBJECT

public:
	void setupUi(QMainWindow* MainWindow, QApplication* app, PartList* partList);

	public slots:
		void UpdatePartTable();

private:
	void SetupQTLayout(QMainWindow* MainWindow);
	void retranslateUi(QMainWindow* MainWindow);  // retranslateUi
	void SetDarkTheme(QApplication* app);
	QString EnumToQStr(Parts::ServerStatus enumm);

	QString EnumToQStr(Parts::BBStatus enumm);

	QStringList CreateQStringListFromPart(Parts::PartInstance& part);

	QTimer m_refreshTimer;
	PartList* m_pPartList;
	const int kUIUpdateTime = 16;  // Milliseconds between UI updates
	QStringList tableHeaders = {"PUID",          "Bin Assignment", "Camera Offset",   "Server Status",
															"Part Status",   "Lego Part #",    "Lego Category #", "Lego Category Name",
															"Time Phile", "Time MTM",  "Time CF",  "Time BB",
															"unused"};

	QAction* actionNew_sorting_rules;
	QAction* actionLoad_sorting_rules;
	QAction* actionSave_sorting_rules;
	QAction* actionSave_sorting_rules_as;
	QAction* actionShutdown_server_and_exit;
	QAction* actionOpen_log_folder;
	QAction* actionAbout;
	QAction* actionHelp;
	QAction* actionInsert_menu_items_here;
	QWidget* centralwidget;
	QVBoxLayout* verticalLayout;
	QVBoxLayout* verticalLayout_2;
	QTabWidget* tabWidget;
	QWidget* tab_sorting;
	QHBoxLayout* horizontalLayout_5;
	QVBoxLayout* verticalLayout_3;
	QLabel* label_5;
	QTableWidget* table_server_log;
	QWidget* tab_active_parts;
	QVBoxLayout* verticalLayout_4;
	QLabel* label_8;
	QTableWidget* table_active_parts;
	QHBoxLayout* horizontalLayout_2;
	QVBoxLayout* verticalLayout_7;
	QLabel* label_2;
	QLabel* label;
	QVBoxLayout* verticalLayout_8;
	QLabel* label_4;
	QLabel* label_3;
	QSpacerItem* horizontalSpacer;
	QVBoxLayout* verticalLayout_5;
	QPushButton* button_start_sorting;
	QPushButton* button_stop_sorting;
	QVBoxLayout* verticalLayout_6;
	QPushButton* button_apply_sorting;
	QPushButton* butto_load_sorting;
	QVBoxLayout* verticalLayout_9;
	QPushButton* pushButton;
	QPushButton* pushButton_2;
	QMenuBar* menubar;
	QStatusBar* statusbar;
	QTimer* refreshTimer;
};

namespace Ui {
    class MainWindow: public UIMainWIndow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // SUIP_H
