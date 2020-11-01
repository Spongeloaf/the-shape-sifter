# 3rd party imports
from typing import List, Any
from sys import argv
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPalette,QColor

# 1st party imports
import ss_classes
from ss_classes import ClientParams, PartInstance, SuipLadle, BbPacket


class SuipWindow(QMainWindow, ):

    # constructor
    def __init__(self, params: ClientParams):
        super().__init__()

        # load settings.ini
        self.tick_rate = params.tick_rate
        self.list_len = params.list_len

        # pipes
        self.pipe_send = params.pipe_send
        self.pipe_recv = params.pipe_recv
        self.pipe_part_list = params.pipe_part_list

        # part list init
        self.part_list = [PartInstance]
        self.list_column_count = 0

        # windows parameters
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
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.table_server_log.sizePolicy().hasHeightForWidth())

        self.table_server_log.setSizePolicy(size_policy)
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

        self.retranslate_ui(self)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(self)


        #start SQL timer. refresh_timer drives the auto-refresh function of the parts DB
        self.refresh_timer = QTimer()

        self.refresh_timer.timeout.connect(self.update_active_part_table)
        self.refresh_timer.start(self.tick_rate)

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "main_window"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sorting), _translate("main_window", "Sorting"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_active_parts), _translate("main_window", "Active Parts"))
        self.button_apply_sorting.setText(_translate("main_window", "Apply Sorting Rules"))
        self.butto_load_sorting.setText(_translate("main_window", "Load Sorting Rules"))
        self.button_stop_sorting.setText(_translate("main_window", "Stop Sorting"))
        self.button_start_sorting.setText(_translate("main_window", "Start Sorting"))
        self.menu_file.setTitle(_translate("main_window", "File"))
        self.menu_edit.setTitle(_translate("main_window", "Edit"))
        self.menu_help.setTitle(_translate("main_window", "Help"))


    def create_active_part_table_widget(self):
        part = PartInstance()
        part_variables = part.__dir__()
        column_names: List[str] = []
        column_count = 0

        for var in part_variables:
            if var.startswith('__'):
                continue
            column_names.append(var)
            column_count += 1

        self.list_column_count = column_count

        # Create table
        table_widget = QTableWidget(self.tab_active_parts)
        table_widget.setRowCount(64)
        table_widget.setColumnCount(column_count)
        table_widget.setHorizontalHeaderLabels(column_names)
        table_widget.move(0, 0)
        table_widget.setObjectName("table_active_parts")
        # table_widget.doubleClicked.connect(ServerInit.on_click)

        return table_widget


    def update_active_part_table(self):
        """Hold on to your butts because there's some shit happening here.
        We are attempting to update a table on the GUI by reading values from the SQL database.
        """

        # bail if there's no new list
        if not self.pipe_part_list.poll(0):
            return

        part_list: list[PartInstance] = self.pipe_part_list.recv()

        for row in range(self.list_len):
            if row < len(part_list):
                column = 0
                for attr, value in part_list[row].__dict__.items():
                    value = str(value)
                    self.table_active_parts.setItem(row, column, QTableWidgetItem(value))
                    column += 1
            else:
                column = 0
                for column in range(self.list_column_count):
                    self.table_active_parts.setItem(row, column, QTableWidgetItem(''))

        # for part in part_list:
        #     column = 0
        #     for attr, value in part.__dict__.items():
        #         value = str(value)
        #         ServerInit.table_active_parts.setItem(row, column, QTableWidgetItem(value))
        #         column += 1
        #     row += 1
        #     if row > 64:
        #         print("Suip part table overflow in update_active_part_table()")
        #         break


    def click_server_control_halt(self):
        ladle = SuipLadle("server_control_halt", "")
        self.pipe_send.send(ladle)


    def click_start_sorting(self):
        ladle = SuipLadle("server_control_run", "")
        self.pipe_send.send(ladle)


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
        All fucntion defs are in suip.py
        The GUI consists of a pyQT gui connected to the active part DB and the part log DB,
        with a pipe to the server for command/control signaling. This signaling is handled by
        a class of objects called ladles. The ladle definition is shape_sifter_tools.py
    """

    suip_app = QApplication(argv)
    set_dark_theme(suip_app)
    suip_window = SuipWindow(client_params)
    suip_window.show()
    suip_window.raise_()
    suip_app.exec_()