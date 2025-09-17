import argparse
import subprocess
import time
import os
import re
import yaml
import sys
import posixpath


# Helper program for CLI argument programming of cave mesh nodes
# Modify config_opt to add more options, only a few are there now
# Usage:
#  python config.py --help 
#
# Get settings from a connected radio and compare to desired settings (COM ports need
# to be changed to your COM port). This will read settings and print out mismatches.
#
# python config.py --port COM3 
# 
# Write settings to radio- after writing/reboot, will read settings and verify
#
# python config.py --port COM3 --set
# The --set command will first read the current settings, compare to desired, and then
# only write out the needed changed settings (channel info is always written). Also,
# the --set command only writes one setting at a time with a reboot in-between because
# writing multiple settings at a time does not seem to be reliable
#
# If you just want to echo the commands that are being executed add the '-t' (--test) flag
# In echo mode, the radio is not contacted
#
# Docs on settings: https://meshtastic.org/docs/configuration/
# Docs on Cli: https://meshtastic.org/docs/software/python/cli/
#
# In set mode, it will write settings, set a new key for the primary channel.
# This always writes data returned from --info command to infofiles/<longname>.txt
# 
# 
# Sample output (read)
# D:\meshtastic\cli>python config.py cave_node.yml --port COM5
# Running command: meshtastic --port COM5 --get bluetooth.mode --get device.role --get lora.hop_limit --get lora.sx126x_rx_boosted_gain --get lora.ignore_mqtt --get lora.override_duty_cycle --get position.gps_enabled --get position.fixed_position --get device.rebroadcast_mode
# Connected to radio
# bluetooth.mode: 2
# device.role: 0
# lora.hop_limit: 10
# lora.sx126x_rx_boosted_gain: True
# lora.ignore_mqtt: True
# lora.override_duty_cycle: True
# position.gps_enabled: False
# position.fixed_position: False
# device.rebroadcast_mode: 2
# Completed getting preferences
# 
# Running command: meshtastic --port COM5 --info
# Found channel 0
# Node info:
# "id": "!aef88d2f",
# "longName": "BobReese",
# "shortName": "BR02",
# "batteryLevel": 101,
#
# sample output (set)
# 
# D:\meshtastic\cli>python config.py --port COM5 cave_node.yml --set
# Running command: meshtastic --port COM5 --get bluetooth.mode --get device.role --get lora.hop_limit --get lora.sx126x_rx_boosted_gain --get lora.ignore_mqtt --get lora.override_duty_cycle --get position.gps_enabled --get position.fixed_position --get device.rebroadcast_mode
# Connected to radio
# bluetooth.mode: 2
# device.role: 0
# lora.hop_limit: 10
# lora.sx126x_rx_boosted_gain: True
# lora.ignore_mqtt: True
# lora.override_duty_cycle: True
# position.gps_enabled: False
# position.fixed_position: False
# device.rebroadcast_mode: 2
# Completed getting preferences
# 
# Beginning set command sequence for changed settings: {'lora.hop_limit': '3', 'lora.override_duty_cycle': 'false'}
# Running command: meshtastic --port COM5 --set lora.hop_limit 3
# Connected to radio
# Set lora.hop_limit to 3
# Writing modified preferences to device
# 
# Wrote a setting, sleeping for 10 seconds for reboot
# Running command: meshtastic --port COM5 --set lora.override_duty_cycle false
# Connected to radio
# Set lora.override_duty_cycle to false
# Writing modified preferences to device
# 
# Wrote a setting, sleeping for 10 seconds for reboot
# Finished, settings, writing channel
# Running command: meshtastic --port COM5 --ch-set psk base64:9Z0jb0WvHgZy1S45NS2okNU5bM0IRlMh7aYMe8C4g+E= --ch-index 0 --reset-nodedb
# Connected to radio
# Writing modified channels to device
# 
# Sleeping for 10 seconds for reboot so can compare
# Running command: meshtastic --port COM5 --get bluetooth.mode --get device.role --get lora.hop_limit --get lora.sx126x_rx_boosted_gain --get lora.ignore_mqtt --get lora.override_duty_cycle --get position.gps_enabled --get position.fixed_position --get device.rebroadcast_mode
# Connected to radio
# bluetooth.mode: 2
# device.role: 0
# lora.hop_limit: 3
# lora.sx126x_rx_boosted_gain: True
# lora.ignore_mqtt: True
# lora.override_duty_cycle: False
# position.gps_enabled: False
# position.fixed_position: False
# device.rebroadcast_mode: 2
# Completed getting preferences
# 
# Running command: meshtastic --port COM5 --info
# Found channel 0
# Node info:
# "id": "!aef88d2f",
# "longName": "BReese02",
# "shortName": "BR02",
# "batteryLevel": 101,
# Wrote info file: info_BReese02.txt
# 
# Version 1.9 - rewrote to send multiple settings, retry 3 times to write
# settings. Also removed reset_nodedb
# Version 1.8 fixed to work with multiple channels
#
#

version = "1.9"
sleep_time = 20
range_test_extra_sleep = 20
infodir = "infofiles"
configdir = "configfiles"
max_retries = 3

config_lookup = {
    "bluetooth.mode" : {"0":"RANDOM_PIN", "1":"FIXED_PIN", "2":"NO_PIN"},
    "position.gps_mode" : {"0":"DISABLED", "1":"ENABLED", "2":"NOT_PRESENT"}, # for 2.6 firmware only
    "device.role" : {"0":"CLIENT",
                     "1":"CLIENT_MUTE", 
                     "2":"ROUTER", 
                     "3":"REPEATER",
                     "4":"TRACKER", 
                     "5":"SENSOR",
                     "11": "ROUTER_LATE"},
    "lora.region" : { 
        "0" : "UNSET",
        "1": "US",
        "2": "EU_433",
        "3": "EU_868",
        "4": "CN",
        "5": "JP",
        "6": "ANZ",
        "7": "ANZ_433",
        "8": "KR",
        "9": "TW",
        "10": "RU",
        "11": "IN",
        "12": "NZ_865",
        "13": "TH",
        "14": "UA_433",
        "15": "UA_868",
        "16": "MY_433",
        "17": "MY_919",
        "18": "SG_923",
        "19": "PH_433",
        "20": "PH_868",
        "21": "PH_915",
        "22": "NP_865",
        "23": "LORA_24",
    },

    "device.rebroadcast_mode" : {"0":"ALL", "1":"ALL_SKIP_DECODING","2":"LOCAL_ONLY","3":"KNOWN_ONLY","4":"NONE","5":"CORE_PORTNUMS_ONLY"},
    "lora.modem_preset" : {"0":"LONG_FAST", 
                           "1":"LONG_SLOW",
                           "2":"VERY_LONG_SLOW",
                           "3":"MEDIUM_SLOW",
                           "4":"MEDIUM_FAST",
                           "5":"SHORT_SLOW",
                           "6":"SHORT_FAST",
                           "8":"SHORT_TURBO",  # for some reason, this jumps to 8. Not sure what '7' is.
                           },
    "serial.baud" : { "1": "BAUD_110",
                      "2": "BAUD_300",
                      "3": "BAUD_600",
                      "4": "BAUD_1200",
                      "5": "BAUD_2400",
                      "6": "BAUD_4800",
                      "7": "BAUD_9600",
                      "8": "BAUD_19200",
                      "9": "BAUD_38400",
                      "10": "BAUD_57600",
                      "11": "BAUD_115200",
                      "12": "BAUD_230400",
                      "13": "BAUD_460800",
                      "13": "BAUD_576000",
                      "13": "BAUD_921600",
        }
}

longname = ""
shortname = ""

def runProgram(args):
    """
    Run a program in a process, wait for it to finish
    """
    proc = subprocess.Popen(args,cwd=os.getcwd())
    while proc.poll() is None:
        time.sleep(1)

def runProgramCaptureOutput(args):
    """
    Run a program in a process, wait for it to finish
    """
    proc = subprocess.run(args,cwd=os.getcwd(),encoding='latin-1',stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def runCmd(cmd, echoOnly=False, silent=False, reboot=False):

    print(f"Running command: {cmd}")
    if not echoOnly:
        args = cmd.split()
        output = runProgramCaptureOutput(args)
        if not silent:
            lines = output.stdout.split('\n')
            for line in lines:
                print (line)
        if reboot:
            print(f"Sleeping for {sleep_time} seconds for reboot.")
            time.sleep(sleep_time)
        return output.stdout
    else:
        return ""

def doCompareSettings(output, config_opts):
    """
    Compare on radio desired settings versus actual settings
    If config_opts is None, just return the settings
    """
    old_settings = {}
    lines = output.split('\n')
    for line in lines:
        if re.match("^Owner:", line):
                words = line.split()
                if len(words) >= 3:
                    longname = words[1].strip()
                    shortname = words[2].strip()
                    shortname = shortname.replace('(','')
                    shortname = shortname.replace(')','')
                    if config_opts is None:
                        old_settings["user.longname"] = longname
                        old_settings["user.shortname"] = shortname
                        continue
                continue
        words = line.split(':')
        if len(words) ==2:
            key = words[0].strip()
            value = words[1].strip()
            if config_opts is None:
                old_settings[key] = value
                continue
            if key == 'security.admin_key':
                continue # cannot compare this
            if key in config_lookup:
                vdict = config_lookup[key]
                if value in vdict:
                    value = vdict[value]
            if key in config_opts and value != config_opts[key]:
                print (f"Mismatch for {key}, expected: {config_opts[key]}, got {value}")
    return old_settings

def getNewSettings(old_settings, config_opts):
    """
    This compares the old_settings to the desired settings, and
    returns a dict that only has the settings that need to be changed
    """
    new_settings = {}
    for key, value in config_opts.items():
        if key not in old_settings:
            continue
        old_value = old_settings[key]
        if key in config_lookup:
            # translate
            vdict = config_lookup[key]
            if old_value in vdict:
                old_value = vdict[old_value]
        if value != old_value:
            # we have a difference, save this
            new_settings[key] = value
    return new_settings



def doCompareChannels(output):
    """
    Does a check that there are two channels, and that the second one is called 'admin'
    """
    foundChannels = False
    found0 = False
    lines = output.split('\n')
    for line in lines:
        if re.match("^Channels:.*", line):
            foundChannels = True
            continue
        if foundChannels:
            line = line.strip()
            if re.search(".*Index 0:.*",line):
                print("Found channel 0")
                found0 = True
                continue

    if not found0:
        print("Did not find channel 0 (primary channel)")
    
def printDeviceInfo(output):
    """
    Print out the small bit of device info that we are interested in.
    Need the id for remote admin
    """

    global longname
    global shortname
    last_longname = ""

    info = "Node info: "
    lines = output.split('\n')
    state = ""
    tmp_info = ""
    for line in lines:
        line = line.strip()
        if state == "":
            if re.match("^Owner:", line):
                words = line.split()
                if len(words) >= 3:
                    longname = words[1].strip()
                    shortname = words[2].strip()
                    shortname = shortname.replace('(','')
                    shortname = shortname.replace(')','')
            if re.match("^\"user\":", line):
                state = "user"
                continue
            if re.match("^\"deviceMetrics\":", line):
                state = "deviceMetrics"
                continue
        elif state == "user":
            if re.match("^\"id\":", line) or re.match("^\"longName\":", line) or  re.match("^\"shortName\":", line):
                tmp_info += f"\n{line}"
                if re.match("^\"longName\":", line):
                    words = line.split(':',1)
                    if len(words) == 2:
                        last_longname = words[1].replace(',','').replace('"','')
                        last_longname = last_longname.strip()
                        if last_longname == longname:
                            info += tmp_info
                            tmp_info = ""
                continue
            if re.match("^\}", line):
                state = ""
                continue
        elif state == "deviceMetrics":
            if re.match("^\"batteryLevel\":", line) and last_longname == longname:
                info += f"\n{line}"
                continue
            if re.match("^\}", line):
                state = ""
                continue
    print(info)
    if longname:
        try:
            if not posixpath.exists(infodir):
                os.mkdir(infodir)
            fname = posixpath.join(infodir, f"info_{longname}.txt")
            with open(fname,"w") as file:
                file.writelines(output)
            print(f"Wrote info file: {fname}")
        except Exception as e:
            print("ERROR: Unexpected error writing file: %s, %s/%s" % (fname, sys.exc_info()[0], e))



def main():

    parser = argparse.ArgumentParser(description=f"Mesh config for cave-comm devices, Version {version}.")
    parser.add_argument('settingsFile',type=str, help="YAML file containing settings, argument is required.")
    parser.add_argument('-ln', '--longname', dest='longname', type=str,
                        default=None,
                        help='long name, optional')
    parser.add_argument('-sn', '--shortname', dest='shortname', type=str,
                        default=None,
                        help='short name, optional')
    parser.add_argument('-cs', '--csvspec', dest='csv', type=str,
                        default=None,
                        help='YML CSV spec file, optional, creates nodes.csv from all files in infofiles dir ')
    parser.add_argument('-p', '--port', dest='port', type=str,
                        default=None,
                        help='com port name, optional, typically COMn')
    parser.add_argument('-t', '--test', action='store_true',
                        help='test, do not actually execute')
    parser.add_argument('-s', '--set',action='store_true',
                        help='write settings')
    parser.add_argument('-rt', '--rangetest',action='store_true',
                        help='do range test')
    parser.add_argument('-ec', '--export-config',action='store_true',
                        help='export config to configfiles/node_<longname>.yml')
    
    
    args = parser.parse_args()

     # start config
    if args.port:
        meshcmd = f"meshtastic --port {args.port}"
    else:
       meshcmd = "meshtastic"

    if args.rangetest:
        count = 1
        while count < 10000:  # arbitrary limit
            cmd = f"{meshcmd} --sendtext rt{count}"
            runCmd(cmd, echoOnly=args.test, reboot=(not args.test))
            time.sleep(range_test_extra_sleep)  # sleep extra time after text
            count +=1
        return

    try:
        with open(args.settingsFile, 'r') as file:
            yml_opts = yaml.safe_load(file) # Use safe_load to prevent arbitrary code execution
    except Exception as e:
        print("ERROR: Unexpected error parsing yml file: %s, %s/%s" % (args.settingsFile, sys.exc_info()[0], e))
            
    channels = yml_opts.get('channels',None)
    config_opts = yml_opts.get('settings',None)
    if channels is None:
        print(f"WARNING: No available channel settings found in {args.settingsFile} file.")
    if config_opts is None:
        print(f"WARNING: No available settings found in {args.settingsFile} file.")


    if args.longname:
        # add special setting so we can compare like other settings
        config_opts["user.longname"] = args.longname
    if args.shortname:
        config_opts["user.shortname"] = args.shortname

    getcmd = meshcmd
    if config_opts:
        for key in config_opts.keys():
            if key == 'security.admin_key':
                    continue
            getcmd += f" --get {key}"

    infocmd = f"{meshcmd} --info"

    device_info = ""

    if not args.set:
        if config_opts:
            output = runCmd(getcmd, echoOnly=args.test, reboot=(not args.test))
            if not args.test:
                doCompareSettings(output, config_opts)
        device_info = runCmd(infocmd, echoOnly=args.test, silent=True)
        if channels:
            if not args.test:
                doCompareChannels(device_info)
        
    else:
        num_retries = 0
        while num_retries < max_retries:
            # Need to do a get so that compare settings
            output = runCmd(getcmd,echoOnly=args.test)
            
            old_settings = {}  # current device settings
            new_settings = {}  # setting that need to be changed
            if not args.test:
                old_settings = doCompareSettings(output, None)
                new_settings = getNewSettings(old_settings, config_opts)
            
            # create the set command
            setcmd = meshcmd
            if len(new_settings) == 0:
                print("No settings have changed, skipping set sequence")
                break
            else:
                print(f"Beginning set command sequence for changed settings: {new_settings}")
                setcmd = meshcmd
                for key,value in new_settings.items():
                    if key == "user.longname":
                        setcmd += f" --set-owner {value}"
                    elif key == "user.shortname":
                        setcmd += f" --set-owner-short {value}"
                    else:
                        setcmd += f" --set {key} {value}"
                runCmd(setcmd, echoOnly=args.test, reboot=(not args.test))
            
            # loop back to top to compare and try again
            num_retries += 1
            
       
        # do channels
        setcmd = meshcmd
        # write each channel
        for cdict in channels:
            setcmd = meshcmd
            setcmd += f" --ch-set name {cdict['name']} --ch-set psk {cdict['psk']} --ch-index {cdict['index']}"
            print(f"Writing channel index: {cdict['index']}")
            runCmd(setcmd, echoOnly=args.test, reboot=(not args.test))
        time.sleep(15)  # extra sleep after channel
        device_info = runCmd(infocmd, echoOnly=args.test, silent=True)
        if channels:
            if not args.test:
                doCompareChannels(device_info)
            
    if not args.test:
        printDeviceInfo(device_info)

    if args.export_config:
        if longname:
            output = runCmd(f"{meshcmd} --export-config", echoOnly=args.test, reboot=(not args.test), silent=True)
            if output and not args.test:
                try:
                    if not posixpath.exists(configdir):
                        os.mkdir(infodir)
                    fname = posixpath.join(infodir, f"node_{longname}.yml")
                    with open(fname,"w") as file:
                        file.writelines(output)
                    print(f"Wrote config file: {fname}")
                except Exception as e:
                    print("ERROR: Unexpected error writing file: %s, %s/%s" % (fname, sys.exc_info()[0], e))
        else:
            print("Unable to write config file as longname not detected in output")


if __name__ == "__main__":
    main()




