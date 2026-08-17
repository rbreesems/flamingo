# Flamingo MeshApp

This is a Meshtastic Desktop app intended for use at Incident Command to replace usage of the Meshtastic Python CLI and/or the Meshtastic phone app. 

This assumes that there is a laptop at Incident Command used for mesh message logging and other IC administrative tasks.

The desktop app has the following advantages over using just the phone app:
- A dedicated log just for mesh messages with timestamps - you do not have to use the log_parse.py utility for parsing the device debug log
- Configurable automated message response that can be tied to a particular channel - this allows rescuers in the cave to ping Incident Command and receive a response, confirming the comm link back to Incident command


## Installation

This assumes a Windows PC; the app should also be compatible with a Linux Desktop that has a Gnome desktop.
This requires Python 3.14 or higher.

- Download this repo and install a Python environment compatible with the `meshtastic` python package (Python 3.14 has been tested with this).
- Open a command window with Python on the path, change to the `meshapp\src` directory, and execute `pip install -r requirements.txt`
- Test the app by executing `python meshmain.py` in the `meshapp\src` directory - if the app window pops up, then success! 


## Usage

The app uses the `Qt` GUI library and is tab-based. The top-level tabs are:

- `Home` - log display, device connection
- `Messages` - send/receive messages
- `Nodes` - display information about known nodes
-  `Settings` - app settings

The first thing to do on first-time app launch is to visit the `Settings` tab, `General` subtab and use the `Browse (Log Dir)` to set the default log directory to a more easily accessible location than the default Windows user temporary directory.  

Then visit the the `Settings` tab, `GUI` subtab and enable Dark Style if desired. Another handy setting is the `Enable Font/Widget Scaling` checkbox if you want to experiment with scaling text/widget size within the app. These settings require an app relaunch in order to take effect.

### Settings location

All settings are saved in the user's home directory to a directory named `.flamingo_meshapp` in a file named `meshapp_config.yml` so that settings persist between app runs.  This directory will also have a file named `meshapp_nodedb.yml` that contains information about known nodes, delete this file when the app is inactive if you want to start with a fresh node database. 

### Device Connection

The `Autoconnect to serial port` setting in `Settings|General` is enabled by default which means that the app will automatically connect to a meshtastic radio via USB serial once it is plugged in.  If there are multiple devices detected then autoconnect will not be performed and the `Connect` button on the `Home` tab must be used to connect to the comm port selected in the combo box to the right of the `Connect` button.

The `Connect` button on the `Home` tab is disabled if the `Autoconnect to serial port` setting in `Settings|General` is checked so uncheck this option in order to use the `Connect` button.

Use the `Close Interface` pushbutton on the `Home` tab to disconnect from the current device.  WARNING - if the `Autoconnect to serial port` setting is enabled, the app will automatically re-connect to the serial device after disconnect.  In this case, the serial cable must be unplugged to keep the device disconnected.

### Logging

Three logs are generated:

- meshappLog_`timestamp` - contains everything that appears in the `Home|SysLog` tab.
- `comport`\_debug_`timestamp` - contains all debug messages from the attached device serial port.  There is a setting in `Settings|General` that allows this to be echoed to the `Home|SysLog` tab but it is recommended to keep this disabled as the large amount of text affects app performance.
- meshappNodeMessages_`timestamp` - contains only text message logging (both channel messages and direct messages).

### Messages

The `Messages` tab is used for sending and display of node messages. A sub-tab is used for each configured channel, and node sub-tabs are created dynamically for direct messages when needed.  The `Input` text field at the bottom of the page is used for sending a message to the selected tab.  To send a Direct Message (DM) to a node that does not yet have a tab, use the `Add DM` button in the bottom right to create a tab for the selected node from the combo box to the right.

The `Enable ENTER to Send Messages` checkbox  in `Settings|General` enables message send after the `Enter` key is pressed instead of having to press the `Send` button. 

### Nodes

The `Nodes` tab displays information about currently known nodes. A right-click menu on a selected node allows a trace route request to be sent to that node; the returned trace route is displayed in the node information.

The right-click menu includes a `Trace Route` option. Once a `Trace Route` is initiated, it will complete and notify
via message in the status bar. You cannot initiate another trace route until the current one completes, or you
use the `Cancel Trace Route` to cancel the current trace route.   Canceling a trace route will close the interface to reset the internal Meshtastic API - the connection will auto-reconnect as long as the AutoConnect option is enabled.  If Autoconnect is not enabled, then you will need to manually reconnect after the Trace Route is canceled.

The right-click menu includes a request telemetry which is a handy way for checking the battery status of a remote node.

### Auto Reply

The `Settings|General` tab has an `Enable Auto Response` check box that provides an auto response (a thumbs up emoji) if the configured keyword is detected as the first word in the message on the selected channel (cannot be channel 0). This is helpful for a remote rescuer to determine if they have a comms link to Incident Command.


## Version Notes:

- V1.0-1.4 -- initial release, compatible with Python 3.11, needed a patch for the Emojii package
- V1.5 - requires Python 3.14, no patching required.  Added `Cancel Trace Route` to right-click node menu.
- V2.0 - updated message tabs to use tree widgets instead of a text edit
- V2.1 - fixed problem with indication of what telemetry returned for what node 

