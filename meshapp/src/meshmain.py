

from meshapp import Ui_MainWindow
import sys
import gc
from pyside_imports import *
import emoji
import logging
import time
import html
import io
from utils import *
import meshtastic.mesh_interface
import queue
import meshtastic.serial_interface
from pubsub import pub

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.core.utils.emoji_fonts import QEmojiFonts
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.widgets.menus.emoji_picker_menu import QEmojiPickerMenu
from qextrawidgets.gui.items import QIconCategoryItem
import qtawesome as qta

from emoji_data_python import emoji_data


BuildNumber = 1.3

if sys.platform.lower().startswith('win'):
    #code that is specific to the Windows platform.
    import ctypes
    #this code from: https://github.com/pyinstaller/pyinstaller/issues/1339


    def hideConsole():
        """
        This function hides the console window in GUI mode. It is necessary for 
        the frozen application because this application can support both command line 
        processing and GUI mode. Therefore, it cannot be run via pythonw.exe.
        """
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            # if you wanted to close the handles...
            #ctypes.windll.kernel32.CloseHandle(whnd)

    def showConsole():
        """
        This function unhides the console window.
        """
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 1)

else:
    #dummy functions for CLI mode
    def hideConsole():
        pass

    def showConsole():
        pass


def getStatusFontSize(textEdit):
    baseSize =  textEdit.font().pointSize()
    newSize = float(baseSize) * 0.8
    return newSize

class MenuWithToolTips(QMenu):
    def __init__(self, *args, **kwargs):
        super(MenuWithToolTips, self).__init__(*args, **kwargs)
        self.installEventFilter(self)

    def eventFilter(self, target, evt):
        if evt.type() == QEvent.ToolTip:
            action = self.actionAt(evt.pos())
            if action:
                toolTip = action.toolTip()
                if toolTip:
                    QToolTip.showText(self.cursor().pos(),toolTip,self)
            return True
        return False

    def addMenuWithToolTips(self,title):
        newMenu = MenuWithToolTips(title)
        self.addMenu(newMenu)
        return newMenu


class StreamToLogger(object):
    """
    This class is a fake file-like stream object that redirects writes to 
    a logger instance. Use this to redirect stderr to our log file.
    """
    def __init__(self, log_level=logging.INFO):
        """
        This function is the constructor for the StreamToLogger class.
        """
        self.log_level = log_level

    def write(self, buf):
        """
        Take lines from the buffer, format them, write to the log file.
        Verbosity is 10 so that these do not appear in the GUI as in some cases, STDERR
        messages are OK
        """
        #we do not want these lines polluting the console output since we should be catching
        #all errors anyway, so verbosity level is 10. We will mark these with a STDERR tag in the log file.
        for line in buf.rstrip().splitlines():
            outputLogMessage("STDERRR - " + line.rstrip(), level=self.log_level,verbosity=10)
        return

    def flush(self):
        return

    def getvalue(self):
        return 0
    
class MeshappStream(io.IOBase):

    def __init__(self, filestream, textEdit):
        self.filestream = filestream
        self.textEdit = textEdit

    def read(self, size=-1):
        # Define how data is retrieved
        return "data"

    def write(self, b):
        # write to both file and the text edit
        orgLen = len(b)
        b = filterColorCode(b)
        self.filestream.write(b)
        if MeshAppContext.deviceLogEchoEnabled:
            b = b.rstrip()
            outputDebugMessageThread(b, self.textEdit)
        return orgLen
    
    def close(self):
        self.filestream.close()

class MeshappLoggerFileHandler(logging.FileHandler):
    """
    Use this wrapper around logging file handler class so that we
    can exit on log file write error.
    """

    def emit(self, record):
        try:
            logging.FileHandler.emit(self,record)
        except Exception as e:
            s = "ERROR: Unexpected Error writing to MeshApp log file, exiting application,  error: %s/%s " % (sys.exc_info()[0], e)
            print(s)
            sys.exit(-1)

class MeshappLoggerHandler(logging.Handler):
    
    def emit(self,record):
        """
        This emits one logging record, called by the global logger
        """
    
        verbosity = MeshAppContext.defaultLogger.verbosity

        #use verbosity to filter 'info' messages only
        if ( record.levelno == logging.INFO and verbosity is not None  and verbosity > MeshAppContext.defaultVerbosity):
            return
        try:
            useTimeStamps = False
            mw = MeshAppContext.mainWindow
            msg = self.format(record)
            if useTimeStamps:
                msg = "%s -- %s" % (time.strftime("%a %b %d %H:%M:%S"),msg)
            if mw is None:
                print(msg)     #print to stdout
            else:
                mt = mw.sysLogTextEdit
                if (record.levelno == logging.ERROR):
                    mt.append("<font color=\"red\"> <b>%s</b> </font>" % html.escape(msg))
                elif (record.levelno == logging.WARNING):
                    mt.append("<font color=\"orange\"> <b>%s</b> </font>" % html.escape(msg))
                else:
                    colorName = getSystemStyleDefaultColorName()
                    mt.append("<font color=\"%s\">%s</font>" % (colorName,html.escape(msg)))
                mt.verticalScrollBar().setValue(mt.verticalScrollBar().maximum())
                doEventProcessing()
        except:
            self.handleError(record)

def configureLogging(logfile=None):
    """
    Configure logging system
    """
    
    logdir = MeshAppContext.getConfigOption('General:LogDirectory', default='')
    if logdir != '':
        logfile = getTemporaryFilename('meshappLog_',dir=logdir)
    else:
        logfile = getTemporaryFilename('meshappLog_',useOsTempDir=True)
    MeshAppContext.logfile = logfile

    topLogger = logging.getLogger('meshapp')
    topLogger.propagate = False
    topLogger.setLevel(logging.DEBUG)
    myhandler = MeshappLoggerHandler()
    myhandler.setLevel(logging.INFO)
    topLogger.addHandler(myhandler)
    fh = MeshappLoggerFileHandler(logfile,mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    topLogger.addHandler(fh)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S %z")
    fh.setFormatter(formatter)
    MeshAppContext.defaultLogger = topLogger
    # the following captures any warnings output by libraries to the log file instead of allowing them to go to STDOUT
    logging.captureWarnings(True)

    sl = StreamToLogger()
    sys.stderr = sl  # redirect stderr to our log file

    MeshAppContext.messageLogger = logging.getLogger('nodeMessages')
    MeshAppContext.messageLogger.setLevel(logging.DEBUG)
    MeshAppContext.messageLogger.propagate = False
    if logdir != '':
        logfile = getTemporaryFilename('meshappNodeMessages_',dir=logdir)
    else:
        logfile = getTemporaryFilename('meshappNodeMessages_',useOsTempDir=True)
    fh = MeshappLoggerFileHandler(logfile,mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    MeshAppContext.messageLogger.addHandler(fh)
    MeshAppContext.messageLogFile = logfile
    return logfile


def onReceive(packet, interface): # called when a packet arrives
    outputLogMessage(f"Received Mesh packet: {packet}")
    # need to do all of this work in the same thread as the main window
    MeshAppContext.mainWindow.addAction([MeshAppContext.mainWindow.handleOnReceive, packet])

def onConnectionEstablished(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # need to do all of this work in the same thread as the main window
    MeshAppContext.mainWindow.addAction([MeshAppContext.mainWindow.handleOnConnectionEstablished])
    

def onConnectionLost(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # need to do all of this work in the same thread as the main window
    MeshAppContext.mainWindow.addAction([MeshAppContext.mainWindow.handleOnConnectionLost])
    

def doTraceRoute(node):
    try:
         MeshAppContext.mainWindow.serialInterface.sendTraceRoute(node.id, MeshAppContext.getMaxHopLimitForTraceRoute())
         outputLogMessage(f"Trace Route wait for node {node.longName} is finished. ", echoStatus=True)
    except Exception as e:
        outputLogMessage(f"ERROR: Traceroute error for node {node.longName}, {str(e)}", level=logging.ERROR, echoStatus=True)
    return

def doRequestTelemetry(node):
    try:
         MeshAppContext.mainWindow.serialInterface.sendTelemetry(
            destinationId=node.id,
            wantResponse=True,
            channelIndex=0,
            telemetryType="device_metrics",
             )
         outputLogMessage(f"Telemetry request  wait for node {node.longName} is finished. ", echoStatus=True)
    except Exception as e:
        outputLogMessage(f"ERROR: Telemetry request error for node {node.longName}, {str(e)}", level=logging.ERROR, echoStatus=True)
    return


class MessageData(object):
    def __init__(self, messageText, id):
        self.id = id
        self.toId = 0 # if this is non-zero, then this is a DM to this id.
        self.messageType = "in"
        self.messageText = messageText
        self.longName = ""   # from longname
        self.startCursor = 0 # beginning of entire message
        self.endCursor = 0  # end of entire message
        self.statusCursor = 0 # beginning of status line
        self.status = None
        self.textEdit = None  # this is the textEdit that this MessageData appears on
        self.fmt = None
        self.ignoreAck = False  # if True, then ignore any other ack packets arriving for this message

    def displayMessageStatus(self, statusText, statusColor=None):
        if statusColor is None:
            statusColor = getLocalUserColor()
        # now need to display the message text
        cursor = self.textEdit.textCursor()
        cursor.setPosition(self.statusCursor)
        cursor.setPosition(self.statusCursor+len(statusText), QTextCursor.KeepAnchor)
        cursor.insertText(statusText)

        # Do formatting
        newSize = getStatusFontSize(self.textEdit)
        if self.fmt is None:
            self.fmt = QTextCharFormat()
        self.fmt.setFontPointSize(newSize)
        self.fmt.setFontUnderline(True)
        #self.fmt.setFontWeight(QFont.Weight.Bold)
        self.fmt.setForeground(QColor(statusColor))
        cursor.setPosition(self.statusCursor+2)
        cursor.setPosition(self.statusCursor+len(statusText), QTextCursor.KeepAnchor)
        cursor.setCharFormat(self.fmt)

        return

class MessagePage(object):

    def __init__(self, textEdit):
        self.textEdit = textEdit
        self.cursorPosition = 0
        self.messages = []  # list of message objects
        self.nextMessageId = 0
        self.eotMarker = "#E_0?+"
        self.statusLine = "                             "
        self.name = ""  #tab name
        self.fmt = None

    def getNextMessageId(self):
        self.nextMessageId += 1
        return self.nextMessageId
    
    def displayMessage(self, messageType, messageText, longName, fromId, packetId=None, wantAck=True):
        
        messageData = MessageData(messageText, self.getNextMessageId())
        messageData.messageType = messageType
        messageData.longName = longName
        messageData.textEdit = self.textEdit
        self.messages.append(messageData)
        messageData.startCursor = self.cursorPosition
        if messageType == "in":
            statusLine = self.statusLine
            preamble = f"IN ({longName})\n{messageText}\n"
        else:
            statusLine = self.statusLine
            preamble = f"OUT ({longName})\n{messageText}\n"
        msgEnd = f"{self.eotMarker}{statusLine}\n"
        totalMessage = f"{preamble}{msgEnd}"
        messageLength = len(totalMessage)
            
        self.textEdit.append(totalMessage)
        # find the actual end of the message, search for self.eotMarker
        cursor = self.textEdit.textCursor()
        pos = messageData.startCursor + len(preamble)
        messageData.statusCursor = pos # this is the start of search, this is default value, will be adjusted if Eot marker found
        endpos = pos + len(msgEnd)  # do not let the search go past this
        foundEot = False
        index = 0
        while (pos < endpos):
            cursor.setPosition(pos)
            c = self.textEdit.document().characterAt(pos)
            if index == 0:
                if c == self.eotMarker[index]:
                    index += 1
            else:
                if c != self.eotMarker[index]:
                    index = 0 # reset search
                else:
                    index += 1
                    if index == len(self.eotMarker):
                        # found the string
                        foundEot = True
                        pos += 1
                        break
            pos += 1
        if foundEot:
            messageData.statusCursor = pos - len(self.eotMarker)  # beginning of status line
            messageData.endCursor =  pos + len(statusLine)+1
            self.cursorPosition = messageData.endCursor+1
        else:
            # did not find EOT. A problem, use default
            messageData.endCursor =  messageData.startCursor + messageLength
            self.cursorPosition = messageData.endCursor+1
        # replace the EOT text with spaces so that it is not visible
        cursor = self.textEdit.textCursor()
        cursor.setPosition(messageData.statusCursor)
        cursor.setPosition(messageData.statusCursor+len(self.eotMarker), QTextCursor.KeepAnchor)
        cursor.insertText("      ")
        
        
        # do formatting
        nodeColor = MeshAppContext.getNodeColor(fromId)
        # set cursor
        cursor = self.textEdit.textCursor()
        cursor.setPosition(messageData.startCursor)
        cursor.setPosition(messageData.startCursor+len(f"IN ({longName}")+1, QTextCursor.KeepAnchor)
        # apply fmt
        if self.fmt is None:
            self.fmt = QTextCharFormat()
        newSize = getStatusFontSize(self.textEdit)
        self.fmt.setFontPointSize(newSize)
        #self.fmt.setFontWeight(QFont.Weight.Bold)
        self.fmt.setForeground(QColor(nodeColor))
        cursor.setCharFormat(self.fmt)
        if messageType == "in":
            # display incoming messages on status bar
            outputStatusMessageMainWindow(f"{self.name}: IN ({longName}): {messageText}")
        if messageType == "out" and wantAck:
            if not (packetId and packetId in MeshAppContext.mainWindow.orphanAcks):
                messageData.displayMessageStatus("  Waiting on ack")

        self.textEdit.verticalScrollBar().setValue(self.textEdit.verticalScrollBar().maximum())
        return messageData
    

class MeshMainWindow(QMainWindow, Ui_MainWindow):

    nodeTypes = ["ROUTER"]

    
    def __init__(self,parent=None):
        """
        This function is the constructor for the MainWindow class.
        """
        super(MeshMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.mainThread = threading.current_thread()  #use this to keep track of main thread
        self.baseTitle = "Flamingo MeshApp"
        

        self.idleTimer = QtCore.QTimer()
        self.idleTimer.setInterval(200)  # poll every 200 ms for events
        # noinspection PyUnresolvedReferences
        self.idleTimer.timeout.connect(self.idleLoop)  # process our own events during idle time, false lint positive
        self.idleTimer.start()
        self.systemDefaultColorName = None
        self.serialPorts = []
        self.maxQueueSize = 100
        self.actionQueue = queue.Queue(100)
        pub.subscribe(onReceive, "meshtastic.receive")
        pub.subscribe(onConnectionEstablished, "meshtastic.connection.established")
        pub.subscribe(onConnectionLost, "meshtastic.connection.lost")
        self.activeTraceRoute = None
        self.debugStream = None
        self.serialInterface = None  # value returned by meshtastic.serial_interface.SerialInterface
        self.count = 0
        self.channelToName = {}
        self.nameToChannel = {}
        self.autoTapbackMessage = emoji.emojize(':thumbs_up:')
        self.itemsOpenedLimit = 1000
        self.itemsClosedLimit = 5000
        self.nodeListIsExpanded = False
        
        # channelMessagePages are Message pages indexed by channel number
        # directMessagePages are Message pages indexed by from nodeId
        # channel 0 text edit always exists and is fixed.
        # Other text edits are dynamically added as channels are discovered
        # or DMs added
        self.channelMessagePages = { 0 : MessagePage(self.ch0TextEdit)}
        self.directMessagePages = {}  # key is always the remote node ID
        self.waitingForAck = {} # key is packet ID, data is MessageData object
        self.orphanAcks = {}  #  for acks not in waitingForAck, value is error reason
        self.ch0TextEdit.setReadOnly(True)

        # populate widget scaling
        for value in ['1.0','1.1','1.2','1.3','1.4','1.5','1.6','1.7','1.8','1.9','2.0']:
            self.widgetScalingComboBox.addItem(value)
        self.widgetScalingComboBox.setCurrentIndex(0)

        for value in ['shortName','longName', 'lastUpdate', 'batteryLevel', 'hops']:
            self.nodesSortByComboBox.addItem(value)
        self.nodesSortByComboBox.setCurrentIndex(0)

        self.closeConnectionDevicePushButton.setDisabled(True)  # only enabled when connected

        # Connect signals
        self.browseDefaultLogDirPushButton.clicked.connect(self.doBrowseDefaultLogDirPushButton)
        self.autoConnectSerialCheckBox.clicked.connect(self.doAutoConnectSerialCheckBox)
        self.enableEnterToSendCheckBox.clicked.connect(lambda x : MeshAppContext.setConfigOption('General:UseEnterToSend', self.enableEnterToSendCheckBox.isChecked() ))
        self.enableDeviceLogEchoCheckBox.clicked.connect(self.doEnableDeviceLogEchoCheckBox)
        self.connectDevicePushButton.clicked.connect(self.doConnectDevicePushButton)
        self.closeConnectionDevicePushButton.clicked.connect(self.doCloseConnectionDevicePushButton)
        self.isConnectedCheckBox.stateChanged.connect(self.doIsConnectedCheckBoxStateChange)
        self.useDarkStylelCheckBox.clicked.connect(self.doUseDarkStylelCheckBox)
        self.enableFontScalingCheckBox.clicked.connect(self.doEnableFontScalingCheckBox)
        self.sendMessageTextEdit.textChanged.connect(self.sendMessageTextChanged)
        self.clearMessagePushButton.clicked.connect(lambda : self.sendMessageTextEdit.clear())
        self.sendMessagePushButton.clicked.connect(self.doSendMessageClicked)
        self.mainTabWidget.currentChanged.connect(self.doMainTabWidgetCurrentChanged)
        self.addDmTabPushButton.clicked.connect(self.doAddDmTabPushButton)
        self.autoTapbackCheckBox.clicked.connect(lambda x : MeshAppContext.setConfigOption('General:AutoTapback', self.autoTapbackCheckBox.isChecked() ))
        self.autoTapbackLineEdit.editingFinished.connect(
            lambda : MeshAppContext.setConfigOption('General:AutoTapbackKeyword', self.autoTapbackLineEdit.text())
            if self.autoTapbackLineEdit.text() else "")
        self.autoTapbackChannelSpinBox.valueChanged.connect(
            lambda x : MeshAppContext.setConfigOption('General:AutoTapbackChannel', x)
        )
        self.nodesFilterLineEdit.textChanged.connect(self.updateNodeListOnSortFilterChange)
        self.hideOldNodesCheckBox.clicked.connect(self.updateNodeListOnSortFilterChange)
        
        
        # Init fields from saved options
        self.doOptionInit()

        # Configure Nodes tab
        self.nodesTreeWidget.setMouseTracking(True)
        self.nodesOpenOneLevelPushButton.clicked.connect(self.doNodeOpenOneLevel)
        self.nodesCloseAllPushButton.clicked.connect(self.doNodeCloseAll)
        
        self.updateNodesTab()
        self.nodesSortByComboBox.currentIndexChanged.connect(self.updateNodeListOnSortFilterChange)
        self.nodesTreeWidget.contextMenuEvent = self.nodesTreeWidgetContextMenuEvent



        # do not connect this until spin Box has been initialized
        self.fontDpiSpinBox.valueChanged.connect(self.doFontDpiSpinBox)
        self.widgetScalingComboBox.currentIndexChanged.connect(self.doWidgetScalingComboBox)

        #emoji config
        self.emoji_picker_menu = QEmojiPickerMenu(self)
        self.emoji_picker = self.emoji_picker_menu.picker()
        self.emoji_picker.picked.connect(self._on_emoji_picked)

        emoji_picker_view = self.emoji_picker.view()
        emoji_picker_delegate = self.emoji_picker.delegate()

        self.tapback_menu = QEmojiPickerMenu(self)
        self.tapback = self.tapback_menu.picker()
        self.tapback.picked.connect(self._on_tapback_picked)

        



        #self.emojisMessageToolButton.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"))
        if MeshAppContext.getConfigOption('GUI:UseDarkStyle', default=False):
            button_color = "cyan"
        else:
            button_color = "blue"
        emoji_icon = qta.icon(
            "fa6s.face-smile",
            color=button_color
           )
        self.emojisMessageToolButton.setIcon(emoji_icon)

        tapback_icon = qta.icon(
            "fa6s.thumbs-up",
            color=button_color
           )
        self.tapbackMessageToolButton.setIcon(tapback_icon)


        self.emojisMessageToolButton.setMenu(self.emoji_picker_menu)
        self.emojisMessageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.tapbackMessageToolButton.setMenu(self.tapback_menu)
        self.tapbackMessageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.actionsMenuData = [
                         {'text': 'Close',
                          'method': self.doClose,
                          'toolTip': 'Close',
                          'statusTip': 'Close'
                          },
        ]

        self.menus = {}
        self.menubar.clear()
        self.menubar.addMenu(self.createMenu('Actions',self.actionsMenuData))

    def handleOnReceive(self, packet): # called when a packet arrives
        outputLogMessage(f"Received Mesh packet: {packet}")
        MeshAppContext.updateNodeDbFromPacket(packet)
        MeshAppContext.handleAckPacket(packet)
        self.handleMessage(packet)

    def handleOnConnectionEstablished(self): # called when we (re)connect to the radio
        # defaults to broadcast, specify a destination ID if you wish
        if  self.serialInterface is None:
            commPort = MeshAppContext.mainWindow.comPortComboBox.currentText()
            outputLogMessage("ERROR: unable to connect to device on COMM port {commPort}. Try re-connecting or power cycling the attached device.", level=logging.ERROR, echoStatus=True)
            return
        shortName = self.serialInterface.getShortName()
        longName = self.serialInterface.getLongName()
        self.addChannels()
        outputLogMessage(f"Connected to meshtastic device: {shortName}/{longName}", echoStatus=True)
        MeshAppContext.addLocalNodeToDb()
        self.isConnectedCheckBox.setChecked(True)

    def handleOnConnectionLost(self): # called when we (re)connect to the radio
        # defaults to broadcast, specify a destination ID if you wish
        outputLogMessage(f"Disconnected from meshtastic device", echoStatus=True)
        MeshAppContext.isMeshConnected = False
        self.isConnectedCheckBox.setChecked(False)
        if self.debugStream is not None:
            try:
                self.serialInterface = None
                self.debugStream.close()
                self.debugStream = None
            except:
                pass


    def doClose(self):
        self.close()
        return
    
    def createMenu(self,name,menuData):
        #aMenu = QMenu(name)
        aMenu = MenuWithToolTips(name)
        self.menus[name] = aMenu
        for item in menuData:
            if isinstance(item,str) and item =='bar':
                aMenu.addSeparator()
            elif isinstance(item,dict):
                itemName = item['text']
                subMenu = item.get('subMenu',None)
                if subMenu:
                    aMenu.addMenu(self.createMenu(itemName,subMenu))
                else:
                    action = aMenu.addAction(itemName)
                    #isCheckable = item.get('isCheckable',False)
                    #action.setCheckable(isCheckable)
                    #if isCheckable:
                    #    configOption = item.get('configOption',None)
                    #    if isinstance(configOption,str):
                    #        action.setChecked(getGlobalConfigData().getSimpleConfigOption(configOption,False))
                    #        #save this action so set checked/unchecked later
                    #        self.checkableActions[configOption] = action

                    if item.get('toolTip', None):
                        action.setToolTip(item.get('toolTip'))
                    if item.get('statusTip', None):
                        action.setStatusTip(item.get('statusTip'))
                    if 'method' in item:
                        action.triggered.connect(item['method'])

        return aMenu

    # Nodes tab

    def nodesTreeWidgetContextMenuEvent(self, event):
        """
        Context menu is displayed on right  click
        """
        itemList = getGetSelectedItemsFromWidget(self.nodesTreeWidget)
        if len(itemList) != 1:
            return
        itemText = itemList[0].text(0)
        words = itemText.split()
        if len(words) != 2:
            return
        
        nodeName = words[0]
        nodeId = convertNodeId(words[1])
        node = MeshAppContext.getNodeById(nodeId)
        if node is None:
            return
        if nodeId == MeshAppContext.localNodeId:
            # no menu items for local node
            outputStatusMessageMainWindow(f"No menu action items for connected node: {nodeName}")
            return
        
        if self.activeTraceRoute:
            # no menu items a traceroute is active
            outputStatusMessageMainWindow(f"Still waiting on last traceroute")
            return

        
        menu = QMenu()
        if not self.activeTraceRoute:
            traceRouteAction = menu.addAction("Trace Route")
        else:
            outputStatusMessageMainWindow(f"Traceroute not available, still waiting on last traceroute.")
        
        telemetryAction = menu.addAction("Request telemetry")
        selectedAction = menu.exec_(event.globalPos())

        if selectedAction is None:
            return

        if selectedAction == traceRouteAction:
            outputStatusMessageMainWindow(f"Sending Trace Route to {nodeName}")
            aThread = threading.Thread(target=doTraceRoute, args=[node])
            aThread.start()
            self.activeTraceRoute = node.id
            return
        elif selectedAction == telemetryAction:
            outputStatusMessageMainWindow(f"Requesting telemetry from {nodeName}")
            aThread = threading.Thread(target=doRequestTelemetry, args=[node])
            aThread.start()
        
        return
    

    def updateNodeListOnSortFilterChange(self):
        try:
            text = self.nodesFilterLineEdit.text()
            
            nodeList = MeshAppContext.getNodeList(filter=text,sort=self.nodesSortByComboBox.currentText(),
                                                  filterOldNodes=self.hideOldNodesCheckBox.isChecked())
            self.updateNodesByNameForWidget(self.nodesTreeWidget, nodeList, 'nodes')
            if self.nodeListIsExpanded:
                self.doNodeOpenOneLevel()
        except Exception as e:
            outputLogMessage("ERROR, unexpected error in updating node view information, error: %s/%s" % (sys.exc_info()[0], e),level=logging.ERROR)
            outputStackTrace(sys.exc_info()[2])

        return


    def updateNodesByNameForWidget(self,targetWidget, nodeList, view, quiet=False,flags=None):
        """
        Update the list of nodes arranged by name in the nodes tab.
        """
        defaultFont, defaultBgBrush, defaultFgBrush = self.getTreeWidgetSettings()
        if len(nodeList) == 0:
            return
        self.nodesTreeWidget.clear()

        nodesTopElement = None
        
        for node in nodeList:
            nodeName = node.getDisplayName()
            if nodeName == str(node.id):
                header = nodeName
            else:
                header = str(node.shortName) + "  " + nodeName
            description = node.description()
            if nodesTopElement is not None:
                nodeLine = QTreeWidgetItem(nodesTopElement, [header])
            else:
                nodeLine = QTreeWidgetItem(targetWidget, [header])
            setDisplayItemDefaults(nodeLine, font=defaultFont, bg=defaultBgBrush, fg=defaultFgBrush)
            if  flags is not None:
                nodeLine.setFlags(flags)
            self.addMoreLineItems(nodeLine, description,font=defaultFont,fg=defaultFgBrush,bg=defaultBgBrush)

    def updateNodesTab(self):
        self.nodesTreeWidget.clear()
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        try:
            text = self.nodesFilterLineEdit.text()
            nodeList = MeshAppContext.getNodeList(filter=text,sort=self.nodesSortByComboBox.currentText(),
                                                  filterOldNodes=self.hideOldNodesCheckBox.isChecked())
            self.updateNodesByNameForWidget(self.nodesTreeWidget, nodeList, 'nodes', flags=flags)
            if self.nodeListIsExpanded:
                self.doNodeOpenOneLevel()
        except Exception as e:
            outputLogMessage("ERROR, unexpected error in updating node view information, error: %s/%s" % (sys.exc_info()[0], e),level=logging.ERROR)
            outputStackTrace(sys.exc_info()[2])
        
        return

    def expandRecurse(self,parent, itemsTraversed, isInvisibleRoot=False):
        """
        Recursive function that expands items under a displayed item in the Nodes tab.
        """

        if not isInvisibleRoot and not parent.isExpanded():
            if parent.childCount() != 0:
                parent.setExpanded(True)
            return itemsTraversed,False
        else:
            childCount = parent.childCount()
            i = 0
            while i != childCount:
                child = parent.child(i)
                itemsTraversed,doAbort = self.expandRecurse(child, itemsTraversed+1)
                if itemsTraversed > self.itemsOpenedLimit or doAbort:
                    return itemsTraversed,True
                i = i + 1

        return itemsTraversed,False

    def doOpenOneLevelPushButtonCommon(self, button, currentTreeWidget, statusMethod=None, isInvisibleRoot=False):

        if statusMethod is None:
            statusMethod = outputStatusMessageMainWindow
        button.setEnabled(False)
        button.setEnabled(False)
        if currentTreeWidget:
            if statusMethod:
                statusMethod("\'Open One Level\' action started...")
            itemsTraversed, expandRecurseAbort = self.expandRecurse(currentTreeWidget, 0, isInvisibleRoot)
            if statusMethod:
                if expandRecurseAbort :
                    statusMethod("Item traversal limit exceeded for \'Open One Level\' action, try a smaller range")
                else:
                    statusMethod("\'Open One Level\' action started...Finished.")
        else:
            if statusMethod:
                statusMethod("No item selected \'Open One Level\' action")
        button.setEnabled(True)
        button.setEnabled(True)
        self.ignoreNodeItemExpanded = False

    def doOpenOneLevel(self, targetWidget, statusMethod=None):
        for i in range(0, targetWidget.topLevelItemCount()):
            thisItem = targetWidget.topLevelItem(i)
            self.doOpenOneLevelPushButtonCommon(
                self.nodesOpenOneLevelPushButton,
                thisItem,
                statusMethod=statusMethod
            )

    def doNodeOpenOneLevel(self):
        self.ignoreItemExpanded = True
        self.nodeListIsExpanded = True
        self.doOpenOneLevel(self.nodesTreeWidget)
        self.ignoreItemExpanded = False

    def closeRecurse(self,parent, itemsTraversed, isInvisibleRoot=False):
        """
        Recursive function that closes items under a displayed item in the Nodes tab.
        :param isInvisibleRoot: specifies whether to skip checking the initial tree widget item's
                                expanded state.
        """

        if isInvisibleRoot or parent.isExpanded():
            childCount = parent.childCount()
            i = 0
            itemsTraversed = itemsTraversed+1
            while i != childCount:
                child = parent.child(i)
                if child.childCount != 0:
                    itemsTraversed, doAbort = self.closeRecurse(child,itemsTraversed)
                if itemsTraversed > self.itemsClosedLimit or doAbort:
                    return itemsTraversed, True
                i = i + 1
            parent.setExpanded(False)
        return itemsTraversed, False


    def doCloseAllPushButtonCommon(self, button, currentTreeWidget, statusMethod=None, isInvisibleRoot=False):
        if statusMethod is None:
            statusMethod = outputStatusMessageMainWindow

        button.setEnabled(False)
        button.setEnabled(False)
        if currentTreeWidget:
            statusMethod("\'Close All\' action started...")
            itemsTraversed, closeRecurseAbort = self.closeRecurse(currentTreeWidget, 0, isInvisibleRoot)
            if closeRecurseAbort:
                statusMethod("Item traversal limit exceeded for \'Close All\' action, try a smaller range")
            else:
                statusMethod("\'Close All\' action started...Finished.")
        else:
            statusMethod("No item selected \'Close All\' action")
        button.setEnabled(True)
        button.setEnabled(True)

    def doCloseAll(self, targetWidget, statusMethod=None):
        for i in range(0, targetWidget.topLevelItemCount()):
            thisItem = targetWidget.topLevelItem(i)
            self.doCloseAllPushButtonCommon(
                self.nodesCloseAllPushButton,
                thisItem,
                statusMethod=statusMethod
            )

    def doNodeCloseAll(self):
        self.doCloseAll(self.nodesTreeWidget)
        self.nodeListIsExpanded = False

    def getTreeWidgetSettings(self):
        defaultFontString = MeshAppContext.getConfigOption('GUI:TreeWidgetFont', default=None)
        if defaultFontString is not None:
            defaultFont = self.font()
            defaultFont.fromString(defaultFontString)
        else:
            defaultFont = None
        defaultBgColor = MeshAppContext.getConfigOption('GUI:TreeWidgetBgFontColor', default=None)
        if defaultBgColor is not None:
            defaultBgBrush = QBrush(QColor(defaultBgColor))
        else:
            defaultBgBrush = None
        defaultFgColor = MeshAppContext.getConfigOption('GUI:TreeWidgetFgFontColor', default=None)
        if defaultFgColor is not None:
            defaultFgBrush = QBrush(QColor(defaultFgColor))
        else:
            defaultFgBrush = None

        return defaultFont,defaultBgBrush,defaultFgBrush

    def addMoreLineItems(self, heading, description,font=None,fg=None,bg=None):
        """
        Utility function for adding more items to the item list displayed in the View Devices tab.
        Items are enabled and selectable, but not draggable.
        """
        for d in description:
            if len(d) == 1:
                item = QTreeWidgetItem(heading, d)
                setDisplayItemDefaults(item, font=font, bg=bg, fg=fg)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            else:
                subheading = QTreeWidgetItem(heading, d.pop(0))
                setDisplayItemDefaults(subheading, font=font, bg=bg, fg=fg)
                subheading.setFlags(QtCore.Qt.ItemIsSelectable |QtCore.Qt.ItemIsEnabled )
                self.addMoreLineItems(subheading, d, font=font,fg=fg,bg=bg)
            doEventProcessing()

    def updateNodeItemDescription(self,nodeItem,node):
        """
        Update this node item description
        :return:
        """

        # delete the children of the nodeItem before adding more.
        i = 0
        childList = []
        while i != nodeItem.childCount():
            childList.append(nodeItem.child(i))
            i += 1
        # now delete children
        for child in childList:
            nodeItem.removeChild(child)
        # now we have to update the current item node text with new items
        defaultFont, defaultBgBrush, defaultFgBrush = self.getTreeWidgetSettings()
        description = node.description()
        setDisplayItemDefaults(nodeItem, font=defaultFont, bg=defaultBgBrush, fg=defaultFgBrush)
        self.addMoreLineItems(nodeItem, description, font=defaultFont, fg=defaultFgBrush, bg=defaultBgBrush)
        return

    def updateNodeTreeWidgets(self,node):
        """
        This nodeId info has been changed, so update the node list for this  node.
        Search for this nodeId in the tree widget
        :param nodeId:
        :return:
        """
       
        #now do the same for the editor node tree widget.
        targetWidget = self.nodesTreeWidget
        for i in range(0, targetWidget.topLevelItemCount()):
            # get toplevel item
            thisItem = targetWidget.topLevelItem(i)
            data = thisItem.data(0, 0)
            words = data.split()
            id = words[len(words) - 1]
            if id == node.id:
                self.updateNodeItemDescription(thisItem, node)
                break

        
    def setMyWindowTitle(self):
        if  MeshAppContext.isMeshConnected:
            self.setWindowTitle(f"{self.baseTitle} - {MeshAppContext.localNodeLongName}")
        else:
            self.setWindowTitle(f"{self.baseTitle} - disconnected")

    def doOptionInit(self):
        self.logDirLineEdit.setText(MeshAppContext.getConfigOption('General:LogDirectory', default=''))
        self.autoConnectSerialCheckBox.setChecked(MeshAppContext.getConfigOption('General:AutoConnect', default=False))
        self.enableEnterToSendCheckBox.setChecked(MeshAppContext.getConfigOption('General:UseEnterToSend', default=False))
        self.enableDeviceLogEchoCheckBox.setChecked(MeshAppContext.getConfigOption('General:EnableDeviceLogEcho', default=False))
        self.connectDevicePushButton.setDisabled(self.autoConnectSerialCheckBox.isChecked())
        MeshAppContext.deviceLogEchoEnabled = self.enableDeviceLogEchoCheckBox.isChecked()
        self.useDarkStylelCheckBox.setChecked(MeshAppContext.getConfigOption('GUI:UseDarkStyle', default=False))
        self.enableFontScalingCheckBox.setChecked(MeshAppContext.getConfigOption('GUI:EnableFontScaling', default=False))
        self.fontDpiSpinBox.setMinimum(20)
        self.fontDpiSpinBox.setMaximum(200)
        self.fontDpiSpinBox.setValue(MeshAppContext.getConfigOption('GUI:FontDpi', default=96))
        widgetScale = MeshAppContext.getConfigOption('GUI:WidgetScale', default=1.0)
        index = self.widgetScalingComboBox.findText(str(widgetScale))
        if index == -1:
            index = 0
        self.widgetScalingComboBox.setCurrentIndex(index)

        self.autoTapbackChannelSpinBox.setMinimum(0)
        self.autoTapbackChannelSpinBox.setMaximum(7)
        self.autoTapbackChannelSpinBox.setValue(MeshAppContext.getConfigOption('General:AutoTapbackChannel', default=0))
        self.autoTapbackCheckBox.setChecked(MeshAppContext.getConfigOption('General:AutoTapback', default=False))
        self.autoTapbackLineEdit.setText(MeshAppContext.getConfigOption('General:AutoTapbackKeyword', default="response"))

        return
    
    def _on_emoji_picked(self, item: QIconItem) -> None:
        self.sendMessageTextEdit.textCursor().insertText(item.data(Qt.ItemDataRole.EditRole))

    def _on_tapback_picked(self, item: QIconItem) -> None:
        self.doSendMessageCore(item.data(Qt.ItemDataRole.EditRole))
        return

    def addAction(self, item):
        if self.actionQueue.full():
            outputLogMessage("Ignoring action queue addition, queue is full", level=logging.ERROR, echoStatus=True)
        else:
            self.actionQueue.put(item)

    def idleLoop(self):
        """
        Called during Idle time of the GUI
        """
        # Print welcome
        if not MeshAppContext.welcomeShown:
            outputLogMessage(f"Welcome to Meshapp, Build {BuildNumber}- logfile is {MeshAppContext.logfile}, Message-only log is {MeshAppContext.messageLogFile}")
            MeshAppContext.welcomeShown = True

        self.count += 1
        if self.count == 5:
            self.count = 0
            if not MeshAppContext.isMeshConnected:
                ports = listSerialPorts()
                if len(ports) > 0:
                    portNameList = []
                    for port in ports:
                        portNameList.append(port['device'])
                    portNameList.sort()
                    if self.serialPorts != portNameList:
                        # update combo box
                        outputStatusMessageMainWindow(f"Found connected serial ports")
                        self.serialPorts = portNameList
                        self.comPortComboBox.clear()
                        for comPort in portNameList:
                            self.comPortComboBox.addItem(comPort)
                    if len(self.serialPorts) == 1 and MeshAppContext.getConfigOption('General:AutoConnect', default=False):
                         # open debug file
                        deviceComPort = self.serialPorts[0]
                        logdir = MeshAppContext.getConfigOption('General:LogDirectory', default='')
                        if logdir != '':
                            debugFile = getTemporaryFilename(f"{deviceComPort}_debug_",dir=logdir)
                        else:
                            debugFile = getTemporaryFilename(f"{deviceComPort}_debug_",useOsTempDir=True)
                        try:
                            ofile = open(debugFile, "w", encoding="utf-8")
                            debugStream = MeshappStream(ofile,self.deviceLogTextEdit)
                        except:
                            debugStream = None
                        self.debugStream = debugStream
                        # try to connect
                        try:
                            self.serialInterface = meshtastic.serial_interface.SerialInterface(devPath=deviceComPort, debugOut=debugStream)
                            MeshAppContext.isMeshConnected = True
                        except Exception as e:
                            outputLogMessage(f"ERROR: error in connecting serial device {sys.exc_info()[0]}/{e}", level=logging.ERROR, echoStatus=True)
                else:
                    outputStatusMessageMainWindow(f"No serial ports connected")
                    self.serialPorts = []
                    self.comPortComboBox.clear()  # clear com port list
        if not self.actionQueue.empty():
            flist = self.actionQueue.get()
            if callable(flist[0]):
                try:
                    flist[0](*flist[1:])  # first item is method, next times are args
                except Exception as e:
                    s = "ERROR: Error calling actionQueue item, method: %s, arguments: %s, error: %s/%s " % (flist[0],flist[1:],sys.exc_info()[0], e)
                    outputLogMessage(s, level=logging.ERROR)
        if len(self.orphanAcks) > 0 and len(self.waitingForAck) > 0:
            foundAck = None
            for requestId, aDict in self.orphanAcks.items():
                if requestId in self.waitingForAck:
                    self.handleMessageAck(requestId, aDict['errorReason'], aDict['fromId'])
                    foundAck = requestId
                    break
            if foundAck:
                self.orphanAcks.pop(foundAck)

        doEventProcessing()

    def doMainTabWidgetCurrentChanged(self, index):
        if self.mainTabWidget.tabText(index) == "Messages":
            self.updateDmTabsComboBox()
        elif self.mainTabWidget.tabText(index) == "Nodes":
            self.updateNodesTab()

    def updateDmTabsComboBox(self):
        # only update if we are connected
        if not MeshAppContext.isMeshConnected:
            return
        
        nameList = []
        for nodeInfo in MeshAppContext.nodeDb.values():
            if nodeInfo.id != MeshAppContext.localNodeId and nodeInfo.longName:
                nameList.append(nodeInfo.longName)
        if len(nameList) > 0:
            # existing tabs
            dmSet = set(list(self.directMessagePages.keys()))
            nameList.sort()
            self.dmTabsComboBox.clear()
            for name in nameList:
                if not (name in dmSet):
                    self.dmTabsComboBox.addItem(name)

    def doAddDmTabPushButton(self):
        if self.dmTabsComboBox.count() == 0:
            return
        nodeLongname = self.dmTabsComboBox.currentText()
        if nodeLongname not in self.directMessagePages:
            # add a tab
            self.addDirectMessageTab(nodeLongname)
            self.dmTabsComboBox.removeItem(self.dmTabsComboBox.currentIndex())
        return
    
    def handleMessageAck(self, requestId, errorReason, fromId):

        messageData = self.waitingForAck.get(requestId, None)
        if messageData is None:
            # save this ack as the ack could come back before we are ready to handle it
            self.orphanAcks[requestId] = { 'errorReason':errorReason, 'fromId' : fromId }
            return
        if messageData.ignoreAck:
            # this is an extra ack, already been acked, ignore
            self.waitingForAck.pop(requestId, None)
            return
            
        statusText = None
        statusColor = getLocalUserColor()
        
        if errorReason == 'NONE':
            if messageData.toId and messageData.toId != fromId:
                # this was DM to node messageData.toId but the ACK packet is from another ode
                statusText = "  Ack by other"
            else:
                statusText = "   Acknowledged "
                messageData.ignoreAck = True
        elif errorReason == 'MAX_RETRANSMIT':
            statusText = "  Max retransmit "
            statusColor = "red"
            messageData.ignoreAck = True
        elif errorReason == 'NO_CHANNEL':
            statusText = "  No channel "
            statusColor = "red"
            messageData.ignoreAck = True
        else:
            statusText = f"  {errorReason} "
            statusColor = "red"
            messageData.ignoreAck = True
        if statusText is None:
            return
        # we got an ack, remove this messageData from the waitingForAck queue
        self.waitingForAck.pop(requestId, None)

        messageData.displayMessageStatus(statusText, statusColor)
    
        

        return

    def doSendMessageClicked(self): 
         self.doSendMessageCore(self.sendMessageTextEdit.toPlainText())
         return
    
    def doSendMessageCore(self, msg, clearText=True):

        if len(msg) > 200:
            msg = msg[0:199]
        wantAck = True
        tabName = self.messagesTabWidget.tabText(self.messagesTabWidget.currentIndex()) # get exposed tab name
        if tabName in self.directMessagePages:
            # this is a direct message, get the from ID of the node
            node = MeshAppContext.getNodeByLongname(tabName)
            if node is None:
                # this tab name may actually be an ID, try this instead
                try:
                    node = MeshAppContext.getNodeById(int(tabName))
                except:
                    pass
            if node is None:
                outputLogMessage("ERROR: node {tabname} cannot be found, unable to send message.", level=logging.ERROR, echoStatus=True)
            packet = self.serialInterface.sendText(msg, node.id, wantAck=wantAck, wantResponse=False)
            messageData = self.directMessagePages[tabName ].displayMessage("out", msg, MeshAppContext.localNodeLongName, MeshAppContext.localNodeId, packetId=packet.id, wantAck=wantAck)
            messageData.toId = node.id
            outputLogMessage(f"Packet waiting for ack: {packet.id} to node {node.id}")
            logNodeMessage(f"DM FROM: {MeshAppContext.localNodeLongName}, TO:{tabName} >> {msg}")
        else:
            # must be a channel message
            channel = self.nameToChannel[tabName]
            packet = self.serialInterface.sendText(msg, '^all', wantAck=wantAck, wantResponse=False, channelIndex=channel)
            # now need to send this to our text edit
            messageData = self.channelMessagePages[channel].displayMessage("out", msg, MeshAppContext.localNodeLongName, MeshAppContext.localNodeId, packetId=packet.id, wantAck=wantAck)
            outputLogMessage(f"Packet waiting for ack: {packet.id}")
            logNodeMessage(f"Channel {tabName} FROM:{MeshAppContext.localNodeLongName} >> {msg}")
        if wantAck:
            self.waitingForAck[packet.id] = messageData
        if clearText:
            self.sendMessageTextEdit.clear()
            
        return


    def sendMessageTextChanged(self):
        count = self.sendMessageTextEdit.document().characterCount()
        if count != 0:
            count -= 1
        self.charCountLineEdit.setText(f"{count}")
        if count > 200:
            outputLogMessage("ERROR: Send text byte count exceeded. The message will be clipped to 200 bytes.", level=logging.ERROR, echoStatus=True)
        else:
            self.statusbar.clearMessage()
        if count != 0 and MeshAppContext.getConfigOption('General:UseEnterToSend', default=False):
            text = self.sendMessageTextEdit.toPlainText()
            if text[len(text)-1] == "\n":
                self.doSendMessageCore(text[0:len(text)-1])


    def addDirectMessageTab(self, tabName):
        textEdit = QTextEdit()
        textEdit.setReadOnly(True)
        self.messagesTabWidget.addTab(textEdit, tabName)
        messagePage = MessagePage(textEdit)
        messagePage.name = tabName
        self.directMessagePages[tabName] = messagePage
        return

    def getDirectMessageTabName(self, remoteId):
        # this will add a message data tab if needed based on remote ID
        remoteNode = MeshAppContext.getNodeById(remoteId)
        if remoteNode is not None and remoteNode.longName:
            tabName = remoteNode.longName
        else:
            tabName = str(remoteId)
        for i in range(self.messagesTabWidget.count()):
            if self.messagesTabWidget.tabText(i) == tabName:
                return tabName # this tab already exists
        # add this tab with a text edit
        self.addDirectMessageTab(tabName)
        return tabName
    
    def setChannelMessageTabName(self, name, channel):
        isChannel0 = channel == 0
        self.channelToName[channel] = name
        self.nameToChannel[name] = channel
        
        if isChannel0:
            # this is the easy case
            self.messagesTabWidget.setTabText(0, name)
        else:
            # iterate through the tabs and check if a tab with this name
            # already exists 
            for i in range(self.messagesTabWidget.count()):
                if self.messagesTabWidget.tabText(i) == name:
                    return  # this tab already exists
            # add this tab with a text edit
            textEdit = QTextEdit()
            textEdit.setReadOnly(True)
            self.messagesTabWidget.addTab(textEdit, name)
            self.channelMessagePages[channel] = MessagePage(textEdit)
        messagePage = self.channelMessagePages[channel]
        messagePage.name = name
        return
    
    def handleMessage(self, packet):
        decoded = packet.get('decoded', None)
        if decoded is None:
            return
        fromId = packet.get('from',None)
        toId = packet.get('to',None)
        portnum = decoded.get('portnum', None)
        if portnum != 'TEXT_MESSAGE_APP':
            return
        payload = decoded.get('payload', None)
        hopStart = packet.get('hopStart', 0)
        hopLimit = packet.get('hopLimit', 0)
        node = MeshAppContext.getNodeById(fromId)
        if node:
            node.hops = hopStart-hopLimit
        if not isBroadcastId(toId):
            if convertNodeId(toId) == MeshAppContext.localNodeId and payload:
                self.displayDirectMessage(payload, fromId, "in")
        else:
            # this is a channel message
            channel = packet.get('channel', 0)
            if payload:
                self.displayChannelMessage(payload, fromId, channel, "in")
                

        return
    
    def displayDirectMessage (self, payload, remoteId, messageType):
        tabName = self.getDirectMessageTabName(remoteId)
        # the tabName is the longName of the node
        messageText = payload.decode("utf-8")
        logNodeMessage(f"DM FROM:{tabName}, TO: {MeshAppContext.localNodeLongName} >> {messageText}")
        self.directMessagePages[tabName].displayMessage(messageType, messageText, tabName , remoteId)
            
    def displayChannelMessage(self, payload, fromId, channel, messageType):
        
        node = MeshAppContext.getNodeById(fromId)
        if node is None:
            longName = 'unknown'
        else:
            longName = node.longName
            if longName == "":
                longName = 'unknown'



        messageText = payload.decode("utf-8")
        self.channelMessagePages[channel].displayMessage(messageType, messageText, longName, fromId)
        channelName =  self.channelMessagePages[channel].name
        logNodeMessage(f"Channel {channelName} FROM:{longName} >> {messageText}")
        if (MeshAppContext.getConfigOption('General:AutoTapback', default=False) and
           MeshAppContext.getConfigOption('General:AutoTapbackChannel', default=0) == channel ) :
            keyword = MeshAppContext.getConfigOption('General:AutoTapbackKeyword', default=False)
            words = messageText.split()
            if len(words) > 0 and words[0].lower() == keyword.lower():
                self.doSendMessageCore(self.autoTapbackMessage, clearText=False)
        

    def addChannels(self):
        """
        Called on Connection
        """
        myNode = self.serialInterface.localNode
        if not myNode.channels:
            return
        index = 0
        for c in myNode.channels:
            name = f"Ch.{index}"
            if (c.settings and c.settings.name):
                name = f"Ch.{index} {c.settings.name}"
                self.setChannelMessageTabName(name, index)
            index += 1
        return
    
    
        

    def doDirBrowse(self, msg, configOption, textControl, default=None):
        
        if configOption is not None:
            lastpath = MeshAppContext.getConfigOption(configOption)
        else:
            lastpath = None
        if lastpath is None or not posixpath.isdir(lastpath):
            dirPath = getHomeDirectory()
        else:
            dirPath = lastpath
        options = QFileDialog.Options()
        # noinspection PyCallByClass
        newDirPath = QFileDialog.getExistingDirectory(self, msg, dirPath, options)

        if configOption is not None:
            if newDirPath:
                # save this off as an option
                MeshAppContext.setConfigOption(configOption, newDirPath)
                if textControl is not None:
                    textControl.setText(newDirPath)
            elif default is not None:
                MeshAppContext.setConfigOption(configOption, default)
                if textControl is not None:
                    textControl.setText(default)
        return newDirPath
    
    def doBrowseDefaultLogDirPushButton(self):
        self.doDirBrowse("Select logging directory",
                            'General:LogDirectory',
                            self.logDirLineEdit)

    def doAutoConnectSerialCheckBox(self):
        MeshAppContext.setConfigOption('General:AutoConnect', self.autoConnectSerialCheckBox.isChecked())
        self.connectDevicePushButton.setDisabled(self.autoConnectSerialCheckBox.isChecked())
        
    def doEnableDeviceLogEchoCheckBox(self):
        MeshAppContext.setConfigOption('General:EnableDeviceLogEcho', self.enableDeviceLogEchoCheckBox.isChecked())
        MeshAppContext.deviceLogEchoEnabled = self.enableDeviceLogEchoCheckBox.isChecked()

    def doUseDarkStylelCheckBox(self):
        MeshAppContext.setConfigOption('GUI:UseDarkStyle', self.useDarkStylelCheckBox.isChecked())

    def doEnableFontScalingCheckBox(self):
        MeshAppContext.setConfigOption('GUI:EnableFontScaling', self.enableFontScalingCheckBox.isChecked())
       
    def doFontDpiSpinBox(self):
        MeshAppContext.setConfigOption('GUI:FontDpi', self.fontDpiSpinBox.value())

    def doWidgetScalingComboBox(self):
        MeshAppContext.setConfigOption('GUI:WidgetScale', float(self.widgetScalingComboBox.currentText()))

    def doConnectDevicePushButton(self):
        comPort = self.comPortComboBox.currentText()
        try:
            self.serialInterface = meshtastic.serial_interface.SerialInterface(devPath=comPort)
            MeshAppContext.isMeshConnected = True
        except Exception as e:
            outputLogMessage(f"ERROR: error in connecting serial device {sys.exc_info()[0]}/{e}", level=logging.ERROR, echoStatus=True)

    def doCloseConnectionDevicePushButton(self):
        if self.serialInterface:
            try:
                self.serialInterface.close()
                MeshAppContext.isMeshConnected = False
            except Exception as e:
                outputLogMessage(f"ERROR: error while disconnecting interface {sys.exc_info()[0]}/{e}", level=logging.ERROR, echoStatus=True)

    def doIsConnectedCheckBoxStateChange(self, state):
        if state == Qt.CheckState.Checked.value:
            # true
            MeshAppContext.isMeshConnected = True
            self.connectDevicePushButton.setDisabled(True)
            self.sendMessagePushButton.setEnabled(True)
            self.comPortComboBox.setDisabled(True)
            self.closeConnectionDevicePushButton.setDisabled(False)
        else:
            MeshAppContext.isMeshConnected = False
            self.connectDevicePushButton.setDisabled(False)
            self.sendMessagePushButton.setEnabled(False)
            self.comPortComboBox.setDisabled(False)
            self.closeConnectionDevicePushButton.setDisabled(True)

        self.setMyWindowTitle()
        return
    
    def closeEvent(self, event):
        MeshAppContext.saveConfigFile()
        MeshAppContext.saveNodeDb()
        event.accept()

    def isTabExposed(self,name):
        return self.mainTabWidget.tabText(self.mainTabWidget.currentIndex()) == name

def initStyle(app):

    exePath = getExecutablePath()
    exePath = exePath.replace('\\', '/')  # change to posix path
    if MeshAppContext.getConfigOption('GUI:UseDarkStyle', default=False):
        stylePath = posixpath.join(exePath,"dark.stylesheet")
    else:
        stylePath = posixpath.join(exePath,"default.stylesheet")
   
    style = None
    if posixpath.isfile(stylePath):
        try:
            infile = open(stylePath, 'r')
            lines = infile.readlines()
            infile.close()
            style = "".join(lines)
        except Exception as e:
            s = "ERROR: Error style sheet: %s, error: %s/%s " % (stylePath, sys.exc_info()[0], e)
            outputLogMessage(s, level=logging.ERROR)
    if style:
        try:
            app.setStyleSheet(style)
        except Exception as e:
            s = "ERROR: Error applying style sheet, error: %s/%s " % (sys.exc_info()[0], e)
            outputLogMessage(s, level=logging.ERROR)

def meshappStart():
    """
    Main entry point for the app
    """

    # disable automatic garbage collection so we can handle it ourselves
    # QT does not do well with automatic GC
    gc.disable()
    if isWindowsOs():
        if getattr(sys, 'frozen', False):
            hideConsole()

    app = QApplication.instance()
    if app is None:
        if MeshAppContext.getConfigOption('GUI:EnableFontScaling', default=False):
            os.environ["QT_SCREEN_SET_FACTOR"]="0"
            os.environ["QT_SCALE_FACTOR"] = str(MeshAppContext.getConfigOption('GUI:WidgetScale'))
            os.environ["QT_FONT_DPI"] = str(MeshAppContext.getConfigOption('GUI:FontDpi'))
        app = QApplication()
        MeshAppContext.mainApp = app

    frame = MeshMainWindow()
    MeshAppContext.mainWindow = frame
    initStyle(app) 
    frame.show()
    configureLogging()

    app.exec_()

    # and at the end
    if isWindowsOs():
        if getattr(sys, 'frozen', False):
            showConsole()


def getExecutablePath():
    """
    Return the executable path of this the python program executing
    """
    if getattr(sys, 'frozen', False):
        #this is frozen
        exePath = getattr(sys, '_MEIPASS', None)
        if re.search(r"_internal$", exePath):
            if isWindowsOs():
                exePath = exePath.replace(r"\_internal","")
            else:
                exePath = exePath.replace(r"/_internal", "")
    else:
        exePath = os.path.realpath(__file__)
        (exePath,tail) = os.path.split(exePath)
    return exePath


def main():

    MeshAppContext.loadConfigFile()
    MeshAppContext.loadNodeDb()
    while (True):

        meshappStart()
        break

    
    sys.exit(0)

#main
if __name__ == '__main__':
    main()
