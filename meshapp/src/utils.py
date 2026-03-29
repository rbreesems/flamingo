

import os
from datetime import datetime
from pathlib import PureWindowsPath
import sys
from datetime import datetime
import posixpath
import tempfile
import threading
import time
import logging
import serial
import yaml
import re
from copy import deepcopy
from deepdiff import DeepDiff

def isBroadcastId(id):
    id = convertNodeId(id)
    return id == 4294967295

def convertNodeId(id):
    if isinstance(id, int):
        return id
    if isinstance(id, str):
        if id[0] == '!':
            try:
                id_int = int(id[1:], 16)
                return id_int
            except Exception as e:
                outputLogMessage("ERROR: Unexpected error converting node id: %s, %s/%s" % (id, sys.exc_info()[0], e), level=logging.ERROR)
        else:
            try:
                id_int = int(id, 10)
                return id_int
            except Exception as e:
                outputLogMessage("ERROR: Unexpected error converting node id: %s, %s/%s" % (id, sys.exc_info()[0], e), level=logging.ERROR)
    outputLogMessage(f"ERROR: expected either int or string for node id: {id}", level=logging.ERROR)
    return id

def filterColorCode(s):
    #the following explains color codes
    #https://www.shellhacks.com/bash-colors/
    #state
    # 0 normal
    # 1 possible start, found \e
    # 2 in esc sequence, looking for m
    #
    state = 0  #state 0, not in escape sequence
    newS = []
    esc = '\x1b'
    for i in range(len(s)):
        c = s[i]
        if c == 0:
            continue
        if state == 0:
            if c == esc:
                state = 1
                continue
            newS.append(c)
        elif state == 1:
            if c == '[':
                #definitely in escape
                state = 2
                continue
            else:
                state = 0
                newS.append(c)
        elif state == 2:
            if c == 'm':
                state = 0
            elif not (c >= '0' and c <= '9'):
                # broken esc sequence
                state = 0
    return "".join(newS)



def repairText(value):
    text = str(value or "")
    if not text:
        return ""

    if "Р" in text or "Ñ" in text:
        for source_encoding in ("cp1251", "latin1"):
            try:
                repaired = text.encode(source_encoding).decode("utf-8")
            except Exception:
                continue
            if repaired and repaired != text:
                text = repaired
                break

    return text

def describeSerialPort(port):
    return {
        "device": str(getattr(port, "device", "") or ""),
        "name": repairText(getattr(port, "name", "") or ""),
        "description": repairText(getattr(port, "description", "") or ""),
        "manufacturer": repairText(getattr(port, "manufacturer", "") or ""),
        "product": repairText(getattr(port, "product", "") or ""),
        "serialNumber": repairText(getattr(port, "serial_number", "") or ""),
        "location": repairText(getattr(port, "location", "") or ""),
        "interface": repairText(getattr(port, "interface", "") or ""),
        "hwid": repairText(getattr(port, "hwid", "") or ""),
        "vid": getattr(port, "vid", None),
        "pid": getattr(port, "pid", None),
    }


def listSerialPorts():
    try:
        from serial.tools import list_ports  # type: ignore
    except Exception:
        return []
    return [describeSerialPort(port) for port in list_ports.comports()]


def doEventProcessing(force=False):
    """
    This function does event processing once a second, but not more often as this impacts performance.

    """
    

    if  MeshAppContext.disableEventProcessingFlag:
        return

    mw = MeshAppContext.mainWindow
    if mw and (mw.mainThread == threading.current_thread()):
        timeNow = time.time()
        if force or (timeNow - MeshAppContext.lastPrintTime > 1):
            # we need to process events at least once per second or else output to main window is too jumpy
            # but do not process them more often or else this impacts performance
            MeshAppContext.mainApp.processEvents()
            MeshAppContext.lastPrintTime = timeNow


def getSystemStyleDefaultColorName():
    mw = MeshAppContext.mainWindow
    if mw is None:
        #this only happens at initial startup when Main window UI elements are being initialized. After the main window is opened, this gets called
        #again during editor, canvas view initialization and the real value is set
        return 'White' #this is a dummy value
    
    if mw.systemDefaultColorName is not None:
        return mw.systemDefaultColorName
    
    pallette = mw.clearCurrentLogWindowPushButton.palette()
    cRole = mw.clearCurrentLogWindowPushButton.foregroundRole()
    defaultColor = pallette.color(cRole)
    mw.systemDefaultColorName = defaultColor.name()
    return mw.systemDefaultColorName

def getHomeDirectory():
    if sys.platform.lower().startswith('win'):
        home_path = PureWindowsPath(os.path.expanduser("~"))
        home_dir = home_path.as_posix()
    else:
        home_dir = os.path.expanduser("~")

    return home_dir


def getUserTempDirectory():
    return None

def getTemporaryFilename(base, ext='txt',useOsTempDir=False, dir=None):

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{base}_{os.getpid()}_{ts}.{ext}"
    if dir is None:
        dirname = getUserTempDirectory()
    else:
        dirname = dir
    if useOsTempDir or dirname is None:
        if sys.platform.lower().startswith('win'):
            winpath = PureWindowsPath(tempfile.gettempdir())
            dirname = winpath.as_posix()
        else:
            dirname = tempfile.gettempdir()
    return posixpath.join(dirname,filename)

def statusMessageCommon(sb,msg,level):
    
    if MeshAppContext.statusMessageSkip == 0:
        if level == logging.ERROR:
            sb.setStyleSheet("color: red;font-weight:bold")
        else:
            sb.setStyleSheet("color: %s;font-weight:normal" % getSystemStyleDefaultColorName())
        sb.showMessage(msg)
    else:
        MeshAppContext.statusMessageSkip(MeshAppContext.statusMessageSkip - 1)
    

def outputStatusMessageMainWindow(msg,mainTab=True,level=logging.INFO):
    """
    This function only updates the status bar, not the log.
    """
    mw = MeshAppContext.mainWindow
    if (mw is not None) and (mw.mainThread == threading.current_thread()):
        #maintab is True by default. Messages only display on status bar
        #when main tab  is exposed. Things like credential test do not
        #want these other messages seen on status bar, overwrites pass/fail message
        if (not mainTab) or (mainTab and mw.isTabExposed(MeshAppContext.homeTabName)):
            statusMessageCommon(mw.statusbar, msg, level)
        doEventProcessing(force=True)


def outputLogMessageThread(msg, verbosity=None, level=logging.INFO, logger=None, echoStatus=False):
    """
    This function is used by a thread other than the main thread to output a log message to the main window or the console.
    """
    mw = MeshAppContext.mainWindow
    if mw is None or (mw.mainThread == threading.current_thread()):
        #either main window not active, or we are in the main thread, ok to print.
        outputLogMessage(msg,verbosity=verbosity,level=level,logger=logger)
    else:
        mw.addAction([outputLogMessage, msg, verbosity, level, logger, echoStatus])

def outputDebugMessage(msg, textEdit):
    textEdit.append(msg)
    textEdit.verticalScrollBar().setValue(textEdit.verticalScrollBar().maximum())
    doEventProcessing()

def outputDebugMessageThread(msg, textEdit):
    mw = MeshAppContext.mainWindow
    if mw is None or (mw.mainThread == threading.current_thread()):
        outputDebugMessage(msg, textEdit)
    else:
        mw.addAction([outputDebugMessage, msg, textEdit])
        

def outputLogMessage(msg, verbosity=None, level=logging.INFO, logger=None, echoStatus=False,statusMethod=None):
    """
    This function outputs a message to the log window (either stdout in command line mode, or GUI main window).
    """
    #first, check if need to use thread version
    
    mw = MeshAppContext.mainWindow
    if level == logging.ERROR:
        MeshAppContext.errorCode = 1
    if (mw is not None) and  (mw.mainThread != threading.current_thread()):
        #have to use different version.
        outputLogMessageThread(msg, verbosity=verbosity, level=level, logger=logger, echoStatus=echoStatus)
    else:
        if logger is None:
            logger = MeshAppContext.defaultLogger
            if logger is not None:
                logger.verbosity = verbosity
                logger.log(level,msg)
        else:
            logger.verbosity = verbosity
            logger.log(level,msg)
    if echoStatus:
        if statusMethod is not None:
            statusMethod(msg,level=level)
        else:
            outputStatusMessageMainWindow(msg, mainTab=False, level=level)

class Node(object):

    def __init__(self, id=""):
        self.id = convertNodeId(id)   #this is always the decimal ID
        self.longName = ""
        self.shortName = ""
        self.role = ""
        self.batteryLevel = 0
        self.voltage = 0
        self.uptimeSeconds = 0
        self.lastUpdate = time.time()


class ActionItem(object): 
    
    def __init__(self, func, posArgs = None, optArgs = None):
        self.func = func
        self.posArgs = posArgs # always a list
        self.optArgs= optArgs  # always a dict

class MeshAppContext(object):

    mainWindow = None
    mainApp = None
    logfile = None
    defaultLogger = None
    defaultVerbosity = 1
    systemDefaultColorName = None
    disableEventProcessingFlag = False
    lastPrintTime = 0
    errorCode = 0
    homeTabName = 'Home'
    statusMessageSkip = 0
    welcomeShown = False
    isMeshConnected = False
    configData = None
    configDataOrg = None
    nodeDb: dict[int, dict] = {}

    @classmethod
    def getConfigOption(self, configOption, default=None):
        if self.configData is None:
            return default
        if not isinstance(self.configData, dict):
            return default
        keylist = configOption.split(':')
        currentDict = self.configData
        value = default
        for i in range(len(keylist)):
            if i == len(keylist) - 1:
                # at last key
                value = currentDict.get(keylist[i], default)
                break
            else:
                currentDict = currentDict.get(keylist[i], None)
                if currentDict is None or not isinstance(currentDict, dict):
                    return default
        return value
    
    @classmethod
    def setConfigOption(self, configOption, value):
        if self.configData is None:
            return
        if not isinstance(self.configData, dict):
            return
        keylist = configOption.split(':')
        currentDict = self.configData
        for i in range(len(keylist)):
            if i == len(keylist) - 1:
                # at last key
                currentDict[keylist[i]] = value
                break
            else:
                currentDict = currentDict.get(keylist[i], None)
                if currentDict is None or not isinstance(currentDict, dict):
                    return
        return
    
    @classmethod
    def getConfigFilePath(self):
        return posixpath.join(getHomeDirectory(), 'meshapp_config.yml')
    
    @classmethod
    def loadConfigFile(self, configFilePath=None):
        if configFilePath is None:
            configFilePath = self.getConfigFilePath()
        if not posixpath.isfile(configFilePath):
            return  #no config data

        try:
            with open(configFilePath, 'r') as file:
                self.configData = yaml.safe_load(file) # Use safe_load to prevent arbitrary code execution
                self.configDataOrg = deepcopy(self.configData)
                print(f"Configdata loaded from {configFilePath}")
        except Exception as e:
            print("ERROR: Unexpected error parsing yml file: %s, %s/%s" % (configFilePath, sys.exc_info()[0], e))
            return

    @classmethod 
    def saveConfigFile(self, configFilePath=None):
        if configFilePath is None:
            configFilePath = self.getConfigFilePath()
        try:
            diffs = DeepDiff(self.configData, self.configDataOrg)
            if len(diffs) > 0:
                with open(configFilePath, 'w') as file:
                    yaml.safe_dump(self.configData,file) # Use safe_load to prevent arbitrary code execution
                
                    print(f"Configdata saved to {configFilePath}")
        except Exception as e:
            print("ERROR: Unexpected error writing yml file: %s, %s/%s" % (configFilePath, sys.exc_info()[0], e))
            return
        
    @classmethod
    def addLocalNodeToDb(self):
        """
        Add the locally connected node to the DB, called on connection
        """
        info = self.mainWindow.serialInterface.getMyNodeInfo()
        id = info.get('num',None)
        if id is None:
            return
        newNode = Node(id=id)
        self.nodeDb[newNode.id] = newNode
        user = info.get('user',None)
        if user:
            newNode.longName = user.get('longName','')
            newNode.shortName = user.get('shortName','')

    @classmethod
    def addEmptyNode(self,id):
        """
        Called when packet arrives for from/to id values
        Add nodes if not in DB, update lastUpdate time
        """
        id = convertNodeId(id)
        if isBroadcastId(id):
            return
        if id not in self.nodeDb:
            self.nodeDb[id] = Node(id=id)
        else:
            self.nodeDb[id].lastUpdate = time.time()

    @classmethod
    def getNodeById(self,id):
        id = convertNodeId(id)
        return self.nodeDb.get(id,None)

    @classmethod
    def updateNodeDbFromPacket(self, packet):
        fromId = packet.get('from',None)
        if fromId:
            self.addEmptyNode(fromId)
        toId = packet.get('to',None)
        if toId:
            self.addEmptyNode(toId)
        decoded = packet.get('decoded', None)
        if decoded is None:
            return
        portnum = decoded.get('portnum', None)
        if portnum == 'TELEMETRY_APP':
            telemetry = decoded.get('telemetry', None)
            if telemetry:
                deviceMetrics = telemetry.get('deviceMetrics', None)
                if deviceMetrics:
                    batteryLevel = deviceMetrics.get('batteryLevel', None)
                    if isinstance(batteryLevel, int):
                        node = self.getNodeById(fromId)
                        if node:
                            node.batteryLevel = batteryLevel
        elif portnum == 'NODEINFO_APP':
            user = decoded.get('user', None)
            if user:
                id = user.get('id',None)
                if id:
                    node = self.getNodeById(id)
                    node.longName = user.get('longName', '')
                    node.shortName = user.get('shortName', '')
                    node.role = user.get('role', '')





            



        
        

    









