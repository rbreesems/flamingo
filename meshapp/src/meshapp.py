# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'meshapp.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QTextEdit, QToolButton, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1057, 618)
        MainWindow.setFocusPolicy(Qt.ClickFocus)
        self.actionLoad_Network = QAction(MainWindow)
        self.actionLoad_Network.setObjectName(u"actionLoad_Network")
        self.actionMerge_Network = QAction(MainWindow)
        self.actionMerge_Network.setObjectName(u"actionMerge_Network")
        self.actionSave_Network_Visualization_subsetOld = QAction(MainWindow)
        self.actionSave_Network_Visualization_subsetOld.setObjectName(u"actionSave_Network_Visualization_subsetOld")
        self.actionCSV_Export = QAction(MainWindow)
        self.actionCSV_Export.setObjectName(u"actionCSV_Export")
        self.actionCSV_Export_Visualization_subset = QAction(MainWindow)
        self.actionCSV_Export_Visualization_subset.setObjectName(u"actionCSV_Export_Visualization_subset")
        self.actionExpand_Rlogin_Data = QAction(MainWindow)
        self.actionExpand_Rlogin_Data.setObjectName(u"actionExpand_Rlogin_Data")
        self.vmdeploymentActionSSheet_Import = QAction(MainWindow)
        self.vmdeploymentActionSSheet_Import.setObjectName(u"vmdeploymentActionSSheet_Import")
        self.vmDeploymentActionGenerateAnsibleFiles = QAction(MainWindow)
        self.vmDeploymentActionGenerateAnsibleFiles.setObjectName(u"vmDeploymentActionGenerateAnsibleFiles")
        self.vmDeploymentActionSSheet_Export = QAction(MainWindow)
        self.vmDeploymentActionSSheet_Export.setObjectName(u"vmDeploymentActionSSheet_Export")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.vmdeploymentActionSheet_Merge = QAction(MainWindow)
        self.vmdeploymentActionSheet_Merge.setObjectName(u"vmdeploymentActionSheet_Merge")
        self.actionVisio_Import = QAction(MainWindow)
        self.actionVisio_Import.setObjectName(u"actionVisio_Import")
        self.vmDeploymentActionSSheetImportGenerateAnsibleFiles = QAction(MainWindow)
        self.vmDeploymentActionSSheetImportGenerateAnsibleFiles.setObjectName(u"vmDeploymentActionSSheetImportGenerateAnsibleFiles")
        self.actionLoad_Network_Directory = QAction(MainWindow)
        self.actionLoad_Network_Directory.setObjectName(u"actionLoad_Network_Directory")
        self.actionSave_Network_DescriptionOld = QAction(MainWindow)
        self.actionSave_Network_DescriptionOld.setObjectName(u"actionSave_Network_DescriptionOld")
        self.actionGenerateVirtualNetworks = QAction(MainWindow)
        self.actionGenerateVirtualNetworks.setObjectName(u"actionGenerateVirtualNetworks")
        self.actionRegenerateVirtualNetworks = QAction(MainWindow)
        self.actionRegenerateVirtualNetworks.setObjectName(u"actionRegenerateVirtualNetworks")
        self.actionSaveNetworkPlottingSubsetOld = QAction(MainWindow)
        self.actionSaveNetworkPlottingSubsetOld.setObjectName(u"actionSaveNetworkPlottingSubsetOld")
        self.actionNormalizeInterfaces = QAction(MainWindow)
        self.actionNormalizeInterfaces.setObjectName(u"actionNormalizeInterfaces")
        self.vmDeploymentActionGenerateCredentials = QAction(MainWindow)
        self.vmDeploymentActionGenerateCredentials.setObjectName(u"vmDeploymentActionGenerateCredentials")
        self.vmDeploymentActionGenerateCredentialsWithAnsible = QAction(MainWindow)
        self.vmDeploymentActionGenerateCredentialsWithAnsible.setObjectName(u"vmDeploymentActionGenerateCredentialsWithAnsible")
        self.vmDeploymentActionGenerateAnsibleFilesWithRestore = QAction(MainWindow)
        self.vmDeploymentActionGenerateAnsibleFilesWithRestore.setObjectName(u"vmDeploymentActionGenerateAnsibleFilesWithRestore")
        self.actionReinitialize = QAction(MainWindow)
        self.actionReinitialize.setObjectName(u"actionReinitialize")
        self.actionConvertScanToNetSpec = QAction(MainWindow)
        self.actionConvertScanToNetSpec.setObjectName(u"actionConvertScanToNetSpec")
        self.actionResourceCalculator = QAction(MainWindow)
        self.actionResourceCalculator.setObjectName(u"actionResourceCalculator")
        self.actionDistToNonDist = QAction(MainWindow)
        self.actionDistToNonDist.setObjectName(u"actionDistToNonDist")
        self.actionNonDistToDist = QAction(MainWindow)
        self.actionNonDistToDist.setObjectName(u"actionNonDistToDist")
        self.actionSave_Network = QAction(MainWindow)
        self.actionSave_Network.setObjectName(u"actionSave_Network")
        self.vmDeploymentActionGenerateAnsibleFilesInMemory = QAction(MainWindow)
        self.vmDeploymentActionGenerateAnsibleFilesInMemory.setObjectName(u"vmDeploymentActionGenerateAnsibleFilesInMemory")
        self.actionClearScanData = QAction(MainWindow)
        self.actionClearScanData.setObjectName(u"actionClearScanData")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionSave_NetworkAsNewFile = QAction(MainWindow)
        self.actionSave_NetworkAsNewFile.setObjectName(u"actionSave_NetworkAsNewFile")
        self.actionSave_Network_Visualization_subset = QAction(MainWindow)
        self.actionSave_Network_Visualization_subset.setObjectName(u"actionSave_Network_Visualization_subset")
        self.actionSave_Network_Text_View = QAction(MainWindow)
        self.actionSave_Network_Text_View.setObjectName(u"actionSave_Network_Text_View")
        self.actionSaveNetworkPlottingSubset = QAction(MainWindow)
        self.actionSaveNetworkPlottingSubset.setObjectName(u"actionSaveNetworkPlottingSubset")
        self.actionHideMapping = QAction(MainWindow)
        self.actionHideMapping.setObjectName(u"actionHideMapping")
        self.actionHideMapping.setCheckable(True)
        self.actionHideVisualization = QAction(MainWindow)
        self.actionHideVisualization.setObjectName(u"actionHideVisualization")
        self.actionHideVisualization.setCheckable(True)
        self.actionHideCredentials = QAction(MainWindow)
        self.actionHideCredentials.setObjectName(u"actionHideCredentials")
        self.actionHideCredentials.setCheckable(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_84 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_84.setObjectName(u"verticalLayout_84")
        self.mainTabWidget = QTabWidget(self.centralwidget)
        self.mainTabWidget.setObjectName(u"mainTabWidget")
        self.homeTab = QWidget()
        self.homeTab.setObjectName(u"homeTab")
        self.verticalLayout_2 = QVBoxLayout(self.homeTab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.clearCurrentLogWindowPushButton = QPushButton(self.homeTab)
        self.clearCurrentLogWindowPushButton.setObjectName(u"clearCurrentLogWindowPushButton")

        self.horizontalLayout_5.addWidget(self.clearCurrentLogWindowPushButton)

        self.line = QFrame(self.homeTab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_5.addWidget(self.line)

        self.connectDevicePushButton = QPushButton(self.homeTab)
        self.connectDevicePushButton.setObjectName(u"connectDevicePushButton")

        self.horizontalLayout_5.addWidget(self.connectDevicePushButton)

        self.comPortComboBox = QComboBox(self.homeTab)
        self.comPortComboBox.setObjectName(u"comPortComboBox")

        self.horizontalLayout_5.addWidget(self.comPortComboBox)

        self.isConnectedCheckBox = QCheckBox(self.homeTab)
        self.isConnectedCheckBox.setObjectName(u"isConnectedCheckBox")

        self.horizontalLayout_5.addWidget(self.isConnectedCheckBox)

        self.connectedDeviceLineEdit = QLineEdit(self.homeTab)
        self.connectedDeviceLineEdit.setObjectName(u"connectedDeviceLineEdit")
        self.connectedDeviceLineEdit.setAcceptDrops(False)
        self.connectedDeviceLineEdit.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.connectedDeviceLineEdit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.horizontalLayout_5.setStretch(6, 6)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.logTabWidget = QTabWidget(self.homeTab)
        self.logTabWidget.setObjectName(u"logTabWidget")
        self.sysLogTab = QWidget()
        self.sysLogTab.setObjectName(u"sysLogTab")
        self.horizontalLayout_3 = QHBoxLayout(self.sysLogTab)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.sysLogTextEdit = QTextEdit(self.sysLogTab)
        self.sysLogTextEdit.setObjectName(u"sysLogTextEdit")
        self.sysLogTextEdit.setAcceptDrops(False)
        self.sysLogTextEdit.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.sysLogTextEdit)

        self.logTabWidget.addTab(self.sysLogTab, "")
        self.deviceLogTab = QWidget()
        self.deviceLogTab.setObjectName(u"deviceLogTab")
        self.horizontalLayout_4 = QHBoxLayout(self.deviceLogTab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.deviceLogTextEdit = QTextEdit(self.deviceLogTab)
        self.deviceLogTextEdit.setObjectName(u"deviceLogTextEdit")

        self.horizontalLayout_4.addWidget(self.deviceLogTextEdit)

        self.logTabWidget.addTab(self.deviceLogTab, "")

        self.verticalLayout_2.addWidget(self.logTabWidget)

        self.mainTabWidget.addTab(self.homeTab, "")
        self.messagesTab = QWidget()
        self.messagesTab.setObjectName(u"messagesTab")
        self.verticalLayout_6 = QVBoxLayout(self.messagesTab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.messagesTabWidget = QTabWidget(self.messagesTab)
        self.messagesTabWidget.setObjectName(u"messagesTabWidget")
        self.ch0Tab = QWidget()
        self.ch0Tab.setObjectName(u"ch0Tab")
        self.verticalLayout_7 = QVBoxLayout(self.ch0Tab)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.ch0TextEdit = QTextEdit(self.ch0Tab)
        self.ch0TextEdit.setObjectName(u"ch0TextEdit")
        self.ch0TextEdit.setAcceptDrops(False)
        self.ch0TextEdit.setReadOnly(True)

        self.verticalLayout_7.addWidget(self.ch0TextEdit)

        self.messagesTabWidget.addTab(self.ch0Tab, "")

        self.verticalLayout_5.addWidget(self.messagesTabWidget)

        self.groupBox = QGroupBox(self.messagesTab)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.sendMessageTextEdit = QTextEdit(self.groupBox)
        self.sendMessageTextEdit.setObjectName(u"sendMessageTextEdit")

        self.verticalLayout_4.addWidget(self.sendMessageTextEdit)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.sendMessagePushButton = QPushButton(self.groupBox)
        self.sendMessagePushButton.setObjectName(u"sendMessagePushButton")

        self.horizontalLayout_6.addWidget(self.sendMessagePushButton)

        self.clearMessagePushButton = QPushButton(self.groupBox)
        self.clearMessagePushButton.setObjectName(u"clearMessagePushButton")

        self.horizontalLayout_6.addWidget(self.clearMessagePushButton)

        self.emojisMessageToolButton = QToolButton(self.groupBox)
        self.emojisMessageToolButton.setObjectName(u"emojisMessageToolButton")

        self.horizontalLayout_6.addWidget(self.emojisMessageToolButton)

        self.tapbackMessageToolButton = QToolButton(self.groupBox)
        self.tapbackMessageToolButton.setObjectName(u"tapbackMessageToolButton")

        self.horizontalLayout_6.addWidget(self.tapbackMessageToolButton)

        self.charCountLineEdit = QLineEdit(self.groupBox)
        self.charCountLineEdit.setObjectName(u"charCountLineEdit")

        self.horizontalLayout_6.addWidget(self.charCountLineEdit)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)

        self.addDmTabPushButton = QPushButton(self.groupBox)
        self.addDmTabPushButton.setObjectName(u"addDmTabPushButton")

        self.horizontalLayout_6.addWidget(self.addDmTabPushButton)

        self.dmTabsComboBox = QComboBox(self.groupBox)
        self.dmTabsComboBox.setObjectName(u"dmTabsComboBox")

        self.horizontalLayout_6.addWidget(self.dmTabsComboBox)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 1)
        self.horizontalLayout_6.setStretch(2, 1)
        self.horizontalLayout_6.setStretch(3, 1)
        self.horizontalLayout_6.setStretch(4, 2)
        self.horizontalLayout_6.setStretch(5, 5)
        self.horizontalLayout_6.setStretch(6, 1)
        self.horizontalLayout_6.setStretch(7, 3)
        self.horizontalLayout_6.setStretch(8, 5)

        self.verticalLayout_4.addLayout(self.horizontalLayout_6)


        self.verticalLayout_5.addWidget(self.groupBox)

        self.verticalLayout_5.setStretch(0, 20)
        self.verticalLayout_5.setStretch(1, 1)

        self.verticalLayout_6.addLayout(self.verticalLayout_5)

        self.mainTabWidget.addTab(self.messagesTab, "")
        self.settingsTab = QWidget()
        self.settingsTab.setObjectName(u"settingsTab")
        self.horizontalLayout_2 = QHBoxLayout(self.settingsTab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.optionsTabWidget = QTabWidget(self.settingsTab)
        self.optionsTabWidget.setObjectName(u"optionsTabWidget")
        self.optionsGeneralTab = QWidget()
        self.optionsGeneralTab.setObjectName(u"optionsGeneralTab")
        self.verticalLayout = QVBoxLayout(self.optionsGeneralTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_66 = QHBoxLayout()
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.configLoadPushButton = QPushButton(self.optionsGeneralTab)
        self.configLoadPushButton.setObjectName(u"configLoadPushButton")

        self.horizontalLayout_66.addWidget(self.configLoadPushButton)

        self.configSavePushButton = QPushButton(self.optionsGeneralTab)
        self.configSavePushButton.setObjectName(u"configSavePushButton")

        self.horizontalLayout_66.addWidget(self.configSavePushButton)

        self.configSaveAsPushButton = QPushButton(self.optionsGeneralTab)
        self.configSaveAsPushButton.setObjectName(u"configSaveAsPushButton")

        self.horizontalLayout_66.addWidget(self.configSaveAsPushButton)

        self.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_66.addItem(self.horizontalSpacer_31)


        self.verticalLayout.addLayout(self.horizontalLayout_66)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.browseDefaultLogDirPushButton = QPushButton(self.optionsGeneralTab)
        self.browseDefaultLogDirPushButton.setObjectName(u"browseDefaultLogDirPushButton")

        self.horizontalLayout.addWidget(self.browseDefaultLogDirPushButton)

        self.logDirLineEdit = QLineEdit(self.optionsGeneralTab)
        self.logDirLineEdit.setObjectName(u"logDirLineEdit")

        self.horizontalLayout.addWidget(self.logDirLineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.autoConnectSerialCheckBox = QCheckBox(self.optionsGeneralTab)
        self.autoConnectSerialCheckBox.setObjectName(u"autoConnectSerialCheckBox")

        self.verticalLayout.addWidget(self.autoConnectSerialCheckBox)

        self.enableDeviceLogEchoCheckBox = QCheckBox(self.optionsGeneralTab)
        self.enableDeviceLogEchoCheckBox.setObjectName(u"enableDeviceLogEchoCheckBox")

        self.verticalLayout.addWidget(self.enableDeviceLogEchoCheckBox)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.autoTapbackCheckBox = QCheckBox(self.optionsGeneralTab)
        self.autoTapbackCheckBox.setObjectName(u"autoTapbackCheckBox")

        self.horizontalLayout_7.addWidget(self.autoTapbackCheckBox)

        self.autoTapbackChannelSpinBox = QSpinBox(self.optionsGeneralTab)
        self.autoTapbackChannelSpinBox.setObjectName(u"autoTapbackChannelSpinBox")

        self.horizontalLayout_7.addWidget(self.autoTapbackChannelSpinBox)

        self.label_3 = QLabel(self.optionsGeneralTab)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_7.addWidget(self.label_3)

        self.autoTapbackLineEdit = QLineEdit(self.optionsGeneralTab)
        self.autoTapbackLineEdit.setObjectName(u"autoTapbackLineEdit")

        self.horizontalLayout_7.addWidget(self.autoTapbackLineEdit)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_6)

        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 1)
        self.horizontalLayout_7.setStretch(2, 1)
        self.horizontalLayout_7.setStretch(3, 3)
        self.horizontalLayout_7.setStretch(4, 10)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.verticalSpacer_4 = QSpacerItem(20, 439, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.optionsTabWidget.addTab(self.optionsGeneralTab, "")
        self.guiTab = QWidget()
        self.guiTab.setObjectName(u"guiTab")
        self.verticalLayout_3 = QVBoxLayout(self.guiTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.useDarkStylelCheckBox = QCheckBox(self.guiTab)
        self.useDarkStylelCheckBox.setObjectName(u"useDarkStylelCheckBox")

        self.verticalLayout_3.addWidget(self.useDarkStylelCheckBox)

        self.enableFontScalingCheckBox = QCheckBox(self.guiTab)
        self.enableFontScalingCheckBox.setObjectName(u"enableFontScalingCheckBox")

        self.verticalLayout_3.addWidget(self.enableFontScalingCheckBox)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.widgetScalingComboBox = QComboBox(self.guiTab)
        self.widgetScalingComboBox.setObjectName(u"widgetScalingComboBox")

        self.horizontalLayout_9.addWidget(self.widgetScalingComboBox)

        self.label_2 = QLabel(self.guiTab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_9.addWidget(self.label_2)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_9.setStretch(0, 1)
        self.horizontalLayout_9.setStretch(1, 1)
        self.horizontalLayout_9.setStretch(2, 20)

        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.fontDpiSpinBox = QSpinBox(self.guiTab)
        self.fontDpiSpinBox.setObjectName(u"fontDpiSpinBox")

        self.horizontalLayout_8.addWidget(self.fontDpiSpinBox)

        self.label = QLabel(self.guiTab)
        self.label.setObjectName(u"label")

        self.horizontalLayout_8.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 1)
        self.horizontalLayout_8.setStretch(2, 20)

        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.verticalSpacer = QSpacerItem(20, 348, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.optionsTabWidget.addTab(self.guiTab, "")

        self.horizontalLayout_2.addWidget(self.optionsTabWidget)

        self.mainTabWidget.addTab(self.settingsTab, "")

        self.verticalLayout_84.addWidget(self.mainTabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1057, 22))
        self.menuDummy = QMenu(self.menubar)
        self.menuDummy.setObjectName(u"menuDummy")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuDummy.menuAction())

        self.retranslateUi(MainWindow)

        self.mainTabWidget.setCurrentIndex(0)
        self.logTabWidget.setCurrentIndex(0)
        self.messagesTabWidget.setCurrentIndex(0)
        self.optionsTabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Flamingo MeshApp", None))
        self.actionLoad_Network.setText(QCoreApplication.translate("MainWindow", u"Open...                          ctrl-O", None))
#if QT_CONFIG(tooltip)
        self.actionLoad_Network.setToolTip(QCoreApplication.translate("MainWindow", u"Load network from an XML file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionLoad_Network.setStatusTip(QCoreApplication.translate("MainWindow", u"Load network from an XML file", None))
#endif // QT_CONFIG(statustip)
        self.actionMerge_Network.setText(QCoreApplication.translate("MainWindow", u"Merge Network", None))
#if QT_CONFIG(statustip)
        self.actionMerge_Network.setStatusTip(QCoreApplication.translate("MainWindow", u"Merge multiple XML network files into one.", None))
#endif // QT_CONFIG(statustip)
        self.actionSave_Network_Visualization_subsetOld.setText(QCoreApplication.translate("MainWindow", u"Save Network As (Visualization subset)", None))
#if QT_CONFIG(statustip)
        self.actionSave_Network_Visualization_subsetOld.setStatusTip(QCoreApplication.translate("MainWindow", u"Save nodes displayed in Visualization tab to an XML file.", None))
#endif // QT_CONFIG(statustip)
        self.actionCSV_Export.setText(QCoreApplication.translate("MainWindow", u"CSV Export", None))
#if QT_CONFIG(statustip)
        self.actionCSV_Export.setStatusTip(QCoreApplication.translate("MainWindow", u"Export to CSV - uses  code from CSV plugin.", None))
#endif // QT_CONFIG(statustip)
        self.actionCSV_Export_Visualization_subset.setText(QCoreApplication.translate("MainWindow", u"CSV Export (Visualization subset)", None))
#if QT_CONFIG(statustip)
        self.actionCSV_Export_Visualization_subset.setStatusTip(QCoreApplication.translate("MainWindow", u"Export to CSV only nodes displayed  in Visualization tab.", None))
#endif // QT_CONFIG(statustip)
        self.actionExpand_Rlogin_Data.setText(QCoreApplication.translate("MainWindow", u"Expand Rlogin Data", None))
        self.vmdeploymentActionSSheet_Import.setText(QCoreApplication.translate("MainWindow", u"SSheet Import", None))
        self.vmDeploymentActionGenerateAnsibleFiles.setText(QCoreApplication.translate("MainWindow", u"Generate Ansible Files (no restore)", None))
#if QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateAnsibleFiles.setStatusTip(QCoreApplication.translate("MainWindow", u"Generate Ansible files from current devices (restoration data not generated).", None))
#endif // QT_CONFIG(statustip)
        self.vmDeploymentActionSSheet_Export.setText(QCoreApplication.translate("MainWindow", u"SSheet Export", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.vmdeploymentActionSheet_Merge.setText(QCoreApplication.translate("MainWindow", u"SSheet Import/Link XML/Generate Ansible Files (restore)", None))
#if QT_CONFIG(tooltip)
        self.vmdeploymentActionSheet_Merge.setToolTip(QCoreApplication.translate("MainWindow", u"Import SSheet, load XML and link SSheet/XML object, then generate Ansible files", None))
#endif // QT_CONFIG(tooltip)
        self.actionVisio_Import.setText(QCoreApplication.translate("MainWindow", u"Visio Import", None))
#if QT_CONFIG(statustip)
        self.actionVisio_Import.setStatusTip(QCoreApplication.translate("MainWindow", u"Import a Visio file.", None))
#endif // QT_CONFIG(statustip)
        self.vmDeploymentActionSSheetImportGenerateAnsibleFiles.setText(QCoreApplication.translate("MainWindow", u"SSheet Import/Generate Ansible Files (no restore)", None))
        self.actionLoad_Network_Directory.setText(QCoreApplication.translate("MainWindow", u"Merge Network (Directory)", None))
#if QT_CONFIG(tooltip)
        self.actionLoad_Network_Directory.setToolTip(QCoreApplication.translate("MainWindow", u"Merge all XML files from a directory", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionLoad_Network_Directory.setStatusTip(QCoreApplication.translate("MainWindow", u"Merge all XML files from a directory", None))
#endif // QT_CONFIG(statustip)
        self.actionSave_Network_DescriptionOld.setText(QCoreApplication.translate("MainWindow", u"Save Network As (Text view)", None))
#if QT_CONFIG(tooltip)
        self.actionSave_Network_DescriptionOld.setToolTip(QCoreApplication.translate("MainWindow", u"Will save network in text format using information available from View Devices tab.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionSave_Network_DescriptionOld.setStatusTip(QCoreApplication.translate("MainWindow", u"Will save network in text format using information available from View Devices tab.", None))
#endif // QT_CONFIG(statustip)
        self.actionGenerateVirtualNetworks.setText(QCoreApplication.translate("MainWindow", u"Auto Generate Virtual Networks", None))
#if QT_CONFIG(tooltip)
        self.actionGenerateVirtualNetworks.setToolTip(QCoreApplication.translate("MainWindow", u"Will auto generate virtual networks for all nodes not connected to one. Useful for physical network scans if routers are not scanned.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionGenerateVirtualNetworks.setStatusTip(QCoreApplication.translate("MainWindow", u"Will auto generate virtual networks for all nodes not connected to one. Useful for physical network scans if routers are not scanned.", None))
#endif // QT_CONFIG(statustip)
        self.actionRegenerateVirtualNetworks.setText(QCoreApplication.translate("MainWindow", u"Regenerate Virtual Networks", None))
#if QT_CONFIG(statustip)
        self.actionRegenerateVirtualNetworks.setStatusTip(QCoreApplication.translate("MainWindow", u"This deletes all virtual  networks and regnerates them; useful after a network merge where there may be duplicates.", None))
#endif // QT_CONFIG(statustip)
        self.actionSaveNetworkPlottingSubsetOld.setText(QCoreApplication.translate("MainWindow", u"Save Network As (Plotting data subset)", None))
        self.actionNormalizeInterfaces.setText(QCoreApplication.translate("MainWindow", u"Normalize Interfaces", None))
#if QT_CONFIG(tooltip)
        self.actionNormalizeInterfaces.setToolTip(QCoreApplication.translate("MainWindow", u"Normalize Interfaces", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionNormalizeInterfaces.setStatusTip(QCoreApplication.translate("MainWindow", u"Interface names will be changed to Eth0, Eth1, etc, with control network as Eth0.", None))
#endif // QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateCredentials.setText(QCoreApplication.translate("MainWindow", u"Generate Netmapper Scan Credentials", None))
#if QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateCredentials.setStatusTip(QCoreApplication.translate("MainWindow", u"Generate Netmapper Scan Credentials (does not use Ansible execution)", None))
#endif // QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateCredentialsWithAnsible.setText(QCoreApplication.translate("MainWindow", u"Generate Netmapper Scan Credentials (use Ansible)", None))
#if QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateCredentialsWithAnsible.setStatusTip(QCoreApplication.translate("MainWindow", u"Use Ansible to generate scan credentials, needed if passwords are vault encoded.", None))
#endif // QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateAnsibleFilesWithRestore.setText(QCoreApplication.translate("MainWindow", u"Generate Ansible Files (with restore)", None))
#if QT_CONFIG(statustip)
        self.vmDeploymentActionGenerateAnsibleFilesWithRestore.setStatusTip(QCoreApplication.translate("MainWindow", u"Generate Ansible files from current devices with restoration data loaded from scanned XML file.", None))
#endif // QT_CONFIG(statustip)
        self.actionReinitialize.setText(QCoreApplication.translate("MainWindow", u"New...(Reinitialize)", None))
#if QT_CONFIG(statustip)
        self.actionReinitialize.setStatusTip(QCoreApplication.translate("MainWindow", u"Reinitialize - clear database, close all windows.", None))
#endif // QT_CONFIG(statustip)
        self.actionConvertScanToNetSpec.setText(QCoreApplication.translate("MainWindow", u"Convert Scan XML to NetSpec XML", None))
        self.actionResourceCalculator.setText(QCoreApplication.translate("MainWindow", u"Resource Calculator", None))
#if QT_CONFIG(statustip)
        self.actionResourceCalculator.setStatusTip(QCoreApplication.translate("MainWindow", u"Opens the resource calculator.", None))
#endif // QT_CONFIG(statustip)
        self.actionDistToNonDist.setText(QCoreApplication.translate("MainWindow", u"Distributed to Non-distributed", None))
#if QT_CONFIG(statustip)
        self.actionDistToNonDist.setStatusTip(QCoreApplication.translate("MainWindow", u"Convert current database from distributed mode to non-distributed mode.", None))
#endif // QT_CONFIG(statustip)
        self.actionNonDistToDist.setText(QCoreApplication.translate("MainWindow", u"Non-Distributed to Distributed", None))
#if QT_CONFIG(statustip)
        self.actionNonDistToDist.setStatusTip(QCoreApplication.translate("MainWindow", u"Convert current database from non-distributed mode to distributed mode.", None))
#endif // QT_CONFIG(statustip)
        self.actionSave_Network.setText(QCoreApplication.translate("MainWindow", u"Save                              ctrl-S", None))
        self.vmDeploymentActionGenerateAnsibleFilesInMemory.setText(QCoreApplication.translate("MainWindow", u"Generate Ansible Files (no restore, in memory)", None))
        self.actionClearScanData.setText(QCoreApplication.translate("MainWindow", u"Clear Scan Data", None))
#if QT_CONFIG(tooltip)
        self.actionClearScanData.setToolTip(QCoreApplication.translate("MainWindow", u"Clears merged scan data from a network spec.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionClearScanData.setStatusTip(QCoreApplication.translate("MainWindow", u"Clears merged scan data from a network spec.", None))
#endif // QT_CONFIG(statustip)
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionSave_NetworkAsNewFile.setText(QCoreApplication.translate("MainWindow", u"New File", None))
        self.actionSave_Network_Visualization_subset.setText(QCoreApplication.translate("MainWindow", u"Visualization Subset", None))
        self.actionSave_Network_Text_View.setText(QCoreApplication.translate("MainWindow", u"Text View", None))
        self.actionSaveNetworkPlottingSubset.setText(QCoreApplication.translate("MainWindow", u"Plotting Data Subset", None))
        self.actionHideMapping.setText(QCoreApplication.translate("MainWindow", u"Hide Mapping", None))
        self.actionHideVisualization.setText(QCoreApplication.translate("MainWindow", u"Hide Visualization", None))
        self.actionHideCredentials.setText(QCoreApplication.translate("MainWindow", u"Hide Credentials", None))
#if QT_CONFIG(tooltip)
        self.clearCurrentLogWindowPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Clears currently exposed log window", None))
#endif // QT_CONFIG(tooltip)
        self.clearCurrentLogWindowPushButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
#if QT_CONFIG(tooltip)
        self.connectDevicePushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Connect to currently selected COM port", None))
#endif // QT_CONFIG(tooltip)
        self.connectDevicePushButton.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
#if QT_CONFIG(tooltip)
        self.comPortComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Detected COM Ports", None))
#endif // QT_CONFIG(tooltip)
        self.isConnectedCheckBox.setText(QCoreApplication.translate("MainWindow", u"isConnected", None))
        self.connectedDeviceLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"connectedDevice", None))
        self.logTabWidget.setTabText(self.logTabWidget.indexOf(self.sysLogTab), QCoreApplication.translate("MainWindow", u"SysLog", None))
        self.logTabWidget.setTabText(self.logTabWidget.indexOf(self.deviceLogTab), QCoreApplication.translate("MainWindow", u"DeviceLog", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.homeTab), QCoreApplication.translate("MainWindow", u"Home", None))
        self.messagesTabWidget.setTabText(self.messagesTabWidget.indexOf(self.ch0Tab), QCoreApplication.translate("MainWindow", u"Ch.0", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Input", None))
#if QT_CONFIG(tooltip)
        self.sendMessagePushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Send message to exposed Message tab", None))
#endif // QT_CONFIG(tooltip)
        self.sendMessagePushButton.setText(QCoreApplication.translate("MainWindow", u"Send", None))
#if QT_CONFIG(tooltip)
        self.clearMessagePushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Clear send message", None))
#endif // QT_CONFIG(tooltip)
        self.clearMessagePushButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
#if QT_CONFIG(tooltip)
        self.emojisMessageToolButton.setToolTip(QCoreApplication.translate("MainWindow", u"Add an emoji to the send message", None))
#endif // QT_CONFIG(tooltip)
        self.emojisMessageToolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.tapbackMessageToolButton.setToolTip(QCoreApplication.translate("MainWindow", u"Tapback - sends a single emoji to the current message tab", None))
#endif // QT_CONFIG(tooltip)
        self.tapbackMessageToolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.charCountLineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"Message byte count", None))
#endif // QT_CONFIG(tooltip)
        self.charCountLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"char count", None))
#if QT_CONFIG(tooltip)
        self.addDmTabPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Add DM tab for selected node if one is not already available", None))
#endif // QT_CONFIG(tooltip)
        self.addDmTabPushButton.setText(QCoreApplication.translate("MainWindow", u"Add DM", None))
#if QT_CONFIG(tooltip)
        self.dmTabsComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Node choice", None))
#endif // QT_CONFIG(tooltip)
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.messagesTab), QCoreApplication.translate("MainWindow", u"Messages", None))
        self.configLoadPushButton.setText(QCoreApplication.translate("MainWindow", u"Load Config", None))
        self.configSavePushButton.setText(QCoreApplication.translate("MainWindow", u"Save Config", None))
        self.configSaveAsPushButton.setText(QCoreApplication.translate("MainWindow", u"Save Config as...", None))
#if QT_CONFIG(tooltip)
        self.browseDefaultLogDirPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Browse to directory to use for log files", None))
#endif // QT_CONFIG(tooltip)
        self.browseDefaultLogDirPushButton.setText(QCoreApplication.translate("MainWindow", u"Browse (Log Dir)", None))
#if QT_CONFIG(tooltip)
        self.autoConnectSerialCheckBox.setToolTip(QCoreApplication.translate("MainWindow", u"Autoconnect if only one serial port is detected", None))
#endif // QT_CONFIG(tooltip)
        self.autoConnectSerialCheckBox.setText(QCoreApplication.translate("MainWindow", u"Autoconnect to serial port", None))
#if QT_CONFIG(tooltip)
        self.enableDeviceLogEchoCheckBox.setToolTip(QCoreApplication.translate("MainWindow", u"Enable echo of device debug output to GUI - warning - adversely affects performance!", None))
#endif // QT_CONFIG(tooltip)
        self.enableDeviceLogEchoCheckBox.setText(QCoreApplication.translate("MainWindow", u"Enable Device Log Echo", None))
#if QT_CONFIG(tooltip)
        self.autoTapbackCheckBox.setToolTip(QCoreApplication.translate("MainWindow", u"Enable channel monitoring for auto response", None))
#endif // QT_CONFIG(tooltip)
        self.autoTapbackCheckBox.setText(QCoreApplication.translate("MainWindow", u"Enable Auto Response", None))
#if QT_CONFIG(tooltip)
        self.autoTapbackChannelSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"Channel to monitor for auto response", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Channel", None))
#if QT_CONFIG(tooltip)
        self.autoTapbackLineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"Keyword (not case sensitive) that triggers auto response, must be first word in messsage. ", None))
#endif // QT_CONFIG(tooltip)
        self.autoTapbackLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"keyword", None))
        self.optionsTabWidget.setTabText(self.optionsTabWidget.indexOf(self.optionsGeneralTab), QCoreApplication.translate("MainWindow", u"General", None))
#if QT_CONFIG(tooltip)
        self.useDarkStylelCheckBox.setToolTip(QCoreApplication.translate("MainWindow", u"Takes effect on restart", None))
#endif // QT_CONFIG(tooltip)
        self.useDarkStylelCheckBox.setText(QCoreApplication.translate("MainWindow", u"Use Dark Style", None))
#if QT_CONFIG(tooltip)
        self.enableFontScalingCheckBox.setToolTip(QCoreApplication.translate("MainWindow", u"Requires GUI restart. If enabled, Widget/Font scaling are based on values below.\n"
"If disabled, values below are ignored and Font/Widget scaling adjust automatically based on screen resolution.\n"
" Results are OS dependent, experiment with different values.", None))
#endif // QT_CONFIG(tooltip)
        self.enableFontScalingCheckBox.setText(QCoreApplication.translate("MainWindow", u"Enable Font/Widget Scaling", None))
#if QT_CONFIG(tooltip)
        self.widgetScalingComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Larger values, larger widgets. Requires GUI restart.", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Widget Scaling", None))
#if QT_CONFIG(tooltip)
        self.fontDpiSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"Larger values, larger font. Requires GUI restart.", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("MainWindow", u"Font DPI", None))
        self.optionsTabWidget.setTabText(self.optionsTabWidget.indexOf(self.guiTab), QCoreApplication.translate("MainWindow", u"GUI", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.settingsTab), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuDummy.setTitle(QCoreApplication.translate("MainWindow", u"Dummy", None))
    # retranslateUi

