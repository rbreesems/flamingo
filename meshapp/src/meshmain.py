

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
import meshtastic
import queue
import meshtastic.serial_interface
from pubsub import pub

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.core.utils.emoji_fonts import QEmojiFonts
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.widgets.menus.emoji_picker_menu import QEmojiPickerMenu
from qextrawidgets.gui.items import QIconCategoryItem

from emoji_data_python import emoji_data




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
    Configure netmapper logging system
    """
    
    logdir = MeshAppContext.getConfigOption('General:LogDirectory', default='')
    if logdir != '':
        logfile = getTemporaryFilename('meshappLog_',dir=logdir)
    else:
        logfile = getTemporaryFilename('meshappLog_',useOsTempDir=True)
    MeshAppContext.logfile = logfile

    topLogger = logging.getLogger('meshapp')
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



    return logfile


def onReceive(packet, interface): # called when a packet arrives
    outputLogMessage(f"Received Mesh packet: {packet}")
    MeshAppContext.updateNodeDbFromPacket(packet)
    MeshAppContext.mainWindow.addAction([MeshAppContext.mainWindow.handleMessage, packet])


def onConnectionEstablished(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    shortName = MeshAppContext.mainWindow.serialInterface.getShortName()
    longName = MeshAppContext.mainWindow.serialInterface.getLongName()
    MeshAppContext.mainWindow.addAction([MeshAppContext.mainWindow.addChannels])
    outputLogMessage(f"Connected to meshtastic device: {shortName}", echoStatus=True)
    MeshAppContext.mainWindow.isConnectedCheckBox.setChecked(True)
    
    MeshAppContext.mainWindow.connectedDeviceLineEdit.setText(f"{shortName} ({longName})")
    MeshAppContext.addLocalNodeToDb()
   
def onConnectionLost(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    outputLogMessage(f"Disconnected from meshtastic device", echoStatus=True)
    MeshAppContext.isMeshConnected = False
    MeshAppContext.mainWindow.isConnectedCheckBox.setChecked(False)
    MeshAppContext.mainWindow.connectedDeviceLineEdit.clear()
    if MeshAppContext.mainWindow.debugStream is not None:
        try:
            MeshAppContext.mainWindow.serialInterface = None
            MeshAppContext.mainWindow.debugStream.close()
            MeshAppContext.mainWindow.debugStream = None
        except:
            pass

def handleMessageAck(argDict):

    return

class MessageData(object):
    def __init__(self, messageText, id):
        self.id = id
        self.fromNodeId = 0  # not sure we need this
        self.messageType = "in"
        self.messageText = messageText
        self.longName = ""   # from longname
        self.startCursor = 0 # beginning of entire message
        self.endCursor = 0  # end of entire message
        self.statusCursor = 0 # beginning of status line
        self.status = None
        self.textEdit = None  # this is the textEdit that this MessageData appears on

class MessagePage(object):

    def __init__(self, textEdit):
        self.textEdit = textEdit
        self.cursorPosition = 0
        self.messages = []  # list of message objects
        self.nextMessageId = 0
        #self.statusLine = "#E#0#t                   "
        self.eotMarker = "#E_0?+"
        self.statusLine = "                             "
        self.fmt = None

    def getNextMessageId(self):
        self.nextMessageId += 1
        return self.nextMessageId
    
    def displayMessage(self, messageType, messageText, longName, fromId):
        
        messageData = MessageData(messageText, self.getNextMessageId())
        messageData.messageType = messageType
        messageData.longName = longName
        messageData.textEdit = self.textEdit
        self.messages.append(messageData)
        messageData.startCursor = self.cursorPosition
        if messageType == "in":
            preamble = f"IN ({longName})\n{messageText}\n"
        else:
            preamble = f"OUT ({longName})\n{messageText}\n"
        msgEnd = f"{self.eotMarker}{self.statusLine}\n"
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
            messageData.endCursor =  pos + len(self.statusLine)+1
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
        self.fmt.setFontWeight(QFont.Weight.Bold)
        self.fmt.setForeground(QColor(nodeColor))
        cursor.setCharFormat(self.fmt)
        outputLogMessage(f"Message: start:{messageData.startCursor}, end: {messageData.endCursor} cursorpos:{self.cursorPosition}")
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
        self.debugStream = None
        self.serialInterface = None  # value returned by meshtastic.serial_interface.SerialInterface
        self.count = 0
        self.channelToName = {}
        self.nameToChannel = {}
        
        # channelTextEdits are text edits indexed by channel number
        # messageTextEdits are text edits indexed by from nodeId
        # channel 0 text edit always exists and is fixed.
        # Other text edits are dynamically added as channels are discovered
        # or DMs added
        self.channelTextEdits = { 0 : MessagePage(self.ch0TextEdit)}
        self.messageTextEdits = {}
        self.waitingForAck = {} # key is packet ID, data is MessageData object

        # populate widget scaling
        for value in ['1.0','1.1','1.2','1.3','1.4','1.5','1.6','1.7','1.8','1.9','2.0']:
            self.widgetScalingComboBox.addItem(value)
        self.widgetScalingComboBox.setCurrentIndex(0)


        # Config
        self.browseDefaultLogDirPushButton.clicked.connect(self.doBrowseDefaultLogDirPushButton)
        self.autoConnectSerialCheckBox.clicked.connect(self.doAutoConnectSerialCheckBox)
        self.enableDeviceLogEchoCheckBox.clicked.connect(self.doEnableDeviceLogEchoCheckBox)
        self.connectDevicePushButton.clicked.connect(self.doConnectDevicePushButton)
        self.isConnectedCheckBox.stateChanged.connect(self.doIsConnectedCheckBoxStateChange)
        self.useDarkStylelCheckBox.clicked.connect(self.doUseDarkStylelCheckBox)
        self.enableFontScalingCheckBox.clicked.connect(self.doEnableFontScalingCheckBox)
        self.sendMessageTextEdit.textChanged.connect(self.sendMessageTextChanged)
        self.clearMessagePushButton.clicked.connect(lambda : self.sendMessageTextEdit.clear())
        self.sendMessagePushButton.clicked.connect(self.doSendMessageClicked)
        #self.emojisMessagePushButton.clicked.connect(self.doEmojisMessagePushButton)
        # Init fields
        self.doOptionInit()
        # do not connect this until spin Box has been initialized
        self.fontDpiSpinBox.valueChanged.connect(self.doFontDpiSpinBox)
        self.widgetScalingComboBox.currentIndexChanged.connect(self.doWidgetScalingComboBox)

        #emoji config
        self.emoji_picker_menu = QEmojiPickerMenu(self)
        self.emoji_picker = self.emoji_picker_menu.picker()

        emoji_picker_view = self.emoji_picker.view()
        emoji_picker_delegate = self.emoji_picker.delegate()

        self.emojisMessageToolButton.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"))
        self.emojisMessageToolButton.setMenu(self.emoji_picker_menu)
        self.emojisMessageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.emoji_picker.picked.connect(self._on_emoji_picked)


    def doOptionInit(self):
        self.logDirLineEdit.setText(MeshAppContext.getConfigOption('General:LogDirectory', default=''))
        self.autoConnectSerialCheckBox.setChecked(MeshAppContext.getConfigOption('General:AutoConnect', default=False))
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

        return
    
    def _on_emoji_picked(self, item: QIconItem) -> None:
        self.sendMessageTextEdit.textCursor().insertText(item.data(Qt.ItemDataRole.EditRole))

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
            outputLogMessage(f"Welcome to Meshapp - logfile is {MeshAppContext.logfile}")
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
        doEventProcessing()

    

    def doSendMessageClicked(self):

         
        #TODO Extend for direct messages
        msg = self.sendMessageTextEdit.toPlainText()
        tabName = self.messagesTabWidget.tabText(self.messagesTabWidget.currentIndex()) # get exposed tab name
        channel = self.nameToChannel[tabName]
        packet = self.serialInterface.sendText(msg, '^all', wantAck=True, wantResponse=False, onResponse=handleMessageAck, channelIndex=channel)
        # now need to send this to our text edit
        outputLogMessage(f"Out packet id: {packet.id}")
        messageData = self.channelTextEdits[channel].displayMessage("out", msg, MeshAppContext.localNodeLongName, MeshAppContext.localNodeId)
        self.waitingForAck[packet.id] = messageData
        self.sendMessageTextEdit.clear()
        return


    def sendMessageTextChanged(self):
        count = self.sendMessageTextEdit.document().characterCount()
        self.charCountLineEdit.setText(f"{count}")

    
    def setMessageTabName(self, name, channel):
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
            self.messagesTabWidget.addTab(textEdit, name)
            self.channelTextEdits[channel] = MessagePage(textEdit)
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
        if not isBroadcastId(toId):
            outputLogMessage("ERROR, direct messages unimplemented.", level=logging.ERROR, echoStatus=True)
            return
        # this is a channel message
        channel = packet.get('channel', 0)
        payload = decoded.get('payload', None)
        if payload:
            self.displayChannelMessage(payload, fromId, channel, "in")
        return
    
    def displayChannelMessage(self, payload, fromId, channel, messageType):
        # TODO Redo this with message objects
        node = MeshAppContext.getNodeById(fromId)
        if node is None:
            longName = 'unknown'
        else:
            longName = node.longName
            if longName == "":
                longName = 'unknown'

        messageText = payload.decode("utf-8")
        self.channelTextEdits[channel].displayMessage(messageType, messageText, longName, fromId)
        
    

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
                self.setMessageTabName(name, index)
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
            interface = meshtastic.serial_interface.SerialInterface(devPath=comPort)
            MeshAppContext.isMeshConnected = True
        except Exception as e:
            outputLogMessage(f"ERROR: error in connecting serial device {sys.exc_info()[0]}/{e}", level=logging.ERROR, echoStatus=True)

    def doIsConnectedCheckBoxStateChange(self, state):
        if state == Qt.CheckState.Checked.value:
            # true
            MeshAppContext.isMeshConnected = True
            self.connectDevicePushButton.setDisabled(True)
            self.sendMessagePushButton.setEnabled(True)
            self.comPortComboBox.setDisabled(True)
        else:
            MeshAppContext.isMeshConnected = False
            self.connectDevicePushButton.setDisabled(False)
            self.sendMessagePushButton.setEnabled(False)
            self.comPortComboBox.setDisabled(False)
        return
    
    def closeEvent(self, event):
        MeshAppContext.saveConfigFile()
        MeshAppContext.saveNodeDb()
        event.accept()

    def isTabExposed(self,name):
        return self.mainTabWidget.tabText(self.mainTabWidget.currentIndex()) == name

def initStyle(app):

    if MeshAppContext.getConfigOption('GUI:UseDarkStyle', default=False):
        exePath = getExecutablePath()
        exePath = exePath.replace('\\', '/')  # change to posix path
        stylePath = posixpath.join(exePath,"dark.stylesheet")
        darkStyle = None
        if posixpath.isfile(stylePath):
            try:
                infile = open(stylePath, 'r')
                lines = infile.readlines()
                infile.close()
                darkStyle = "".join(lines)
            except Exception as e:
                s = "ERROR: Error style sheet: %s, error: %s/%s " % (stylePath, sys.exc_info()[0], e)
                outputLogMessage(s, level=logging.ERROR)
        if darkStyle:
            try:
                app.setStyleSheet(darkStyle)
            except Exception as e:
                s = "ERROR: Error applying dark style sheet, error: %s/%s " % (sys.exc_info()[0], e)
                outputLogMessage(s, level=logging.ERROR)

def meshappStart():
    """
    Main entry point for the app
    """

    # disable automatic garbage collection so we can handle it ourselves
    # QT does not do well with automatic GC
    #gc.disable()
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
