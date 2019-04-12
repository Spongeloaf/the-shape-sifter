from typing import List, Any
from sys import argv
import shape_sifter_tools as ss
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPalette,QColor


class SuipWindow(QMainWindow, ):

    #constructor
    def __init__(self, active_part_db_fname_const, pipe_me_recv, pipe_me_send,):
        super().__init__()

        # load settings.ini
        pass

        # pipes
        self.pipe_me_send = pipe_me_send
        self.pipe_me_recv = pipe_me_recv

        # init SQL.
        self.active_part_db = sqlite3.connect(active_part_db_fname_const)
        self.sql_curr = self.active_part_db.cursor()

        self.setObjectName("MainWindow")
        self.resize(862, 665)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_sorting = QtWidgets.QWidget()
        self.tab_sorting.setObjectName("tab_sorting")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.tab_sorting)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.table_sorting_rules = QtWidgets.QTableWidget(self.tab_sorting)
        self.table_sorting_rules.setObjectName("table_sorting_rules")
        self.table_sorting_rules.setColumnCount(0)
        self.table_sorting_rules.setRowCount(0)
        self.horizontalLayout_4.addWidget(self.table_sorting_rules)
        self.table_sort_log = QtWidgets.QTableWidget(self.tab_sorting)
        self.table_sort_log.setObjectName("table_sort_log")
        self.table_sort_log.setColumnCount(0)
        self.table_sort_log.setRowCount(0)
        self.horizontalLayout_4.addWidget(self.table_sort_log)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.table_server_log = QtWidgets.QTableWidget(self.tab_sorting)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table_server_log.sizePolicy().hasHeightForWidth())

        self.table_server_log.setSizePolicy(sizePolicy)
        self.table_server_log.setObjectName("table_server_log")
        self.table_server_log.setColumnCount(0)
        self.table_server_log.setRowCount(0)
        self.verticalLayout_3.addWidget(self.table_server_log)
        self.horizontalLayout_5.addLayout(self.verticalLayout_3)
        self.tabWidget.addTab(self.tab_sorting, "")
        self.tab_active_parts = QtWidgets.QWidget()
        self.tab_active_parts.setObjectName("tab_active_parts")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_active_parts)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.table_active_parts = self.create_active_part_table_widget()
        self.verticalLayout_4.addWidget(self.table_active_parts)

        self.tabWidget.addTab(self.tab_active_parts, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.button_apply_sorting = QtWidgets.QPushButton(self.centralwidget)
        self.button_apply_sorting.setObjectName("button_apply_sorting")
        self.horizontalLayout_2.addWidget(self.button_apply_sorting)
        self.butto_load_sorting = QtWidgets.QPushButton(self.centralwidget)
        self.butto_load_sorting.setObjectName("butto_load_sorting")
        self.horizontalLayout_2.addWidget(self.butto_load_sorting)
        self.button_stop_sorting = QtWidgets.QPushButton(self.centralwidget)

        self.button_stop_sorting.setObjectName("button_stop_sorting")
        self.button_stop_sorting.clicked.connect(self.click_server_control_halt)
        self.horizontalLayout_2.addWidget(self.button_stop_sorting)
        self.button_start_sorting = QtWidgets.QPushButton(self.centralwidget)

        self.button_start_sorting.setObjectName("button_start_sorting")
        self.button_start_sorting.clicked.connect(self.click_start_sorting)
        self.horizontalLayout_2.addWidget(self.button_start_sorting)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 862, 21))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_edit = QtWidgets.QMenu(self.menubar)
        self.menu_edit.setObjectName("menu_edit")
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setObjectName("menu_help")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_edit.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.retranslateUi(self)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(self)

        #start SQL timer. sql_timer drives the auto-refresh function of the parts DB
        self.sql_timer = QTimer()
        self.sql_timer.timeout.connect(self.update_active_part_table)
        #self.sql_timer.timeout.connect(self.update_part_tables(self.sql_curr,'table_bin_config'))
        #self.sql_timer.timeout.connect(self.update_part_tables(self.sql_curr,'table_part_log'))
        self.sql_timer.start(250)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sorting), _translate("MainWindow", "Sorting"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_active_parts), _translate("MainWindow", "Active Parts"))
        self.button_apply_sorting.setText(_translate("MainWindow", "Apply Sorting Rules"))
        self.butto_load_sorting.setText(_translate("MainWindow", "Load Sorting Rules"))
        self.button_stop_sorting.setText(_translate("MainWindow", "Stop Sorting"))
        self.button_start_sorting.setText(_translate("MainWindow", "Start Sorting"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.menu_edit.setTitle(_translate("MainWindow", "Edit"))
        self.menu_help.setTitle(_translate("MainWindow", "Help"))

    def create_active_part_table_widget(self):
        #get sql info
        column_names: List[str] = []
        column_count = -1
        for row in self.sql_curr.execute("PRAGMA table_info(active_part_db)"):
            column_names.append(row[1])
            column_count += 1

        # the row returned from sql is a tuple, so we convert to a list, and drop the first item using slice notation
        column_names = list(column_names[1:])
        print(column_names)
        # Create table
        tableWidget = QTableWidget(self.tab_active_parts)
        tableWidget.setRowCount(64)
        tableWidget.setColumnCount(column_count)
        tableWidget.setHorizontalHeaderLabels(column_names)
        tableWidget.move(0, 0)
        tableWidget.setObjectName("table_active_parts")
        #tableWidget.doubleClicked.connect(self.on_click)
        return tableWidget

    def update_active_part_table(self):
        """Hold on to your butts because there's some shit happening here.
        We are attempting to update a table on the GUI by reading values from the SQL database.
        """
        # We begin by initializing a row count at 0 because I haven't found a way to loop through rows in pyQT.
        row_num = 0

        # loop through the whole DB
        for row in self.sql_curr.execute("SELECT * FROM active_part_db"):

            # the row returned from sql is a tuple, so we convert to a list, and drop the first item using slice notation
            row = list(row[1:])

            # we need to fill each column of the GUI row individually, so we get the number of columns
            column = len(row)

            # loop through the columns adding each value individually.
            for column in range(0, column, 1):
                value = str(row[column])
                self.table_active_parts.setItem(row_num, column, QTableWidgetItem(value))

            row_num += 1

    def click_server_control_halt(self):
        ladle = ss.suip_ladle("server_control_halt","")
        self.pipe_me_send.send(ladle)

    def click_start_sorting(self):
        ladle = ss.suip_ladle("server_control_run","")
        self.pipe_me_send.send(ladle)


def set_dark_theme(qApp):
    WHITE = QColor(255, 255, 255)
    BLACK = QColor(0, 0, 0)
    RED = QColor(255, 0, 0)
    PRIMARY = QColor(53, 53, 53)
    SECONDARY = QColor(35, 35, 35)
    TERTIARY = QColor(42, 130, 218)

    qApp.setStyle("Fusion")

    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, WHITE)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, WHITE)
    dark_palette.setColor(QPalette.ToolTipText, WHITE)
    dark_palette.setColor(QPalette.Text, WHITE)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, WHITE)
    dark_palette.setColor(QPalette.BrightText, RED)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, BLACK)

    qApp.setPalette(dark_palette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def main(client_params):
    """ The sorting machine UI
        All fucntion defs are in shape_sifter_gui.py
        The GUI consists of a pyQT gui connected to the active part DB and the part log DB,
        with a pipe to the server for command/control signaling. This signaling is handled by
        a class of objects called ladles. The ladle definition is shape_sifter_tools.py
    """

    suip_app = QApplication(argv)
    set_dark_theme(suip_app)
    suip_window = SuipWindow(client_params.server_db_fname_const, client_params.pipe_recv, client_params.pipe_send, )
    suip_window.show()
    suip_window.raise_()
    suip_app.exec_()