import argparse
import subprocess
import time
import os
import re
import yaml
import sys
import posixpath
from pathlib import Path
from dataclasses import dataclass
import datetime

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
# Version 1.8 fixed to work with multiple channels
#
#


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




# Helper program to parse serial log files from testing
# into one csv file

version = "1.1"
infodir = "infofiles"

columns_name_dict = {}  # key is column_name, value is column_data_key
column_list = []  # list of column names

node_data = {}  # key is short name, value is data dict that maps column_data_key to column_name

log_data = []
surface_node = "BReese01"


@dataclass
class LogEntry:

    tstamp: str
    txhost: str
    inmsg: str
    outmsg: str
    num_hops: int = 0
    

#hop_limit:31, hop_start:31

def parseOneLogFile(fpath):
    global log_data
    global prefs_dict

    ifile = open(fpath,'r')
    lines = ifile.readlines()
    ifile.close()
    for line in lines:
        line = line.rstrip()
        line = filterColorCode(line)
        if re.search(".*Received text msg.*",line):
            
            words = line.split()
            tstamp = words[2]
            cwords = line.split(',')
            host = cwords[2].split('=')[1]
            outmsg = ""
            inmsg = ""
            txhost = ""
            if host == surface_node:
                outmsg = cwords[6].split('=')[1]
            else:
                inmsg = cwords[6].split('=')[1]
                txhost = host

            hop_start = int(cwords[5].split(':')[1])
            hop_limit = int(cwords[4].split(':')[1])
            num_hops = hop_start - hop_limit
            entry = LogEntry(tstamp, txhost, inmsg, outmsg, num_hops)
            if host == surface_node:
                print(f"{entry.tstamp} \t\t\t\t\tOutgoing:  {entry.outmsg}")
            else:
                print(f"{entry.tstamp} Incoming:  {entry.inmsg} \t host: {entry.txhost}  numhops: {entry.num_hops}")



def addColumn(uname, colname):
    global columns_name_dict
    global column_list

    column_list.append(uname)
    columns_name_dict[uname] = colname

def makeCsvFile():
    global node_data
    global prefs_dict
    global columns_name_dict
    global column_list

    ofile = open("nodes.csv","w")
    s = ""
    for uname in column_list:
        s += f"{columns_name_dict[uname]},"
    ofile.write(f"{s}\n")
    for node_dict in node_data.values():
        s = ""
        for uname in column_list:
            v = node_dict.get(uname,None)
            s += f"{v},"
        ofile.write(f"{s}\n")
    ofile.close()

def main():
    global columns_name_dict
    global column_list
    global prefs_dict
    parser = argparse.ArgumentParser(description=f"Parse serial logs from cave testing, Version {version}.")
    parser.add_argument('logdir',type=str, help="Log directory containing log files, all files will parsed.")


    
    args = parser.parse_args()
    
    if not posixpath.isdir(args.logdir):
         print("ERROR: first argument has to specify directory containing log files")
         return
    count = 0
    for entry in sorted(Path(args.logdir).iterdir(), key=os.path.getmtime):
        if entry.is_file():
            parseOneLogFile(posixpath.join(args.logdir,entry.name))
            

    return

    try:

        with open(args.configFile, 'r') as file:
            yml_opts = yaml.safe_load(file) # Use safe_load to prevent arbitrary code execution
    except Exception as e:
        print("ERROR: Unexpected error parsing yml file: %s, %s/%s" % (args.configFile, sys.exc_info()[0], e))

    fixed_cols = yml_opts.get('fixed_cols',None)
    if fixed_cols is None:
        print(f"ERROR, expecting 'fixed_cols' dict that has list of fixed columns in file: {args.configFile}, exiting.")
        return -1
    
    for v in fixed_cols:
        words = v.split(':')
        if len(words)==1:
            addColumn(f"global_{v}",v)
        else:
            addColumn(f"global_{words[0].strip()}", words[1].strip())
       

    prefs = yml_opts.get('prefs',None)
    if prefs is None:
        print(f"ERROR, expecting 'prefs' dict that has dicts of key data to parse: {args.configFile}, exiting.")
        return -1
    
    prefs_dict = prefs
    
    topkeys = sorted(list(prefs.keys()))
    for topkey in topkeys:
        moddict = prefs[topkey]
        ckeys = sorted(list(moddict.keys()))
        for ckey in ckeys:
            addColumn(f"{topkey}_{ckey}", moddict[ckey])

    # column data has been created, now need to parse info files
    if (not posixpath.isdir(infodir)):
        print(f"ERROR, cannot find directory {infodir} that contains node info files, exiting.")
        return
    filelist = os.listdir(infodir)
    for file in filelist:
        fpath = posixpath.join(infodir, file)
        if posixpath.isfile(fpath):
            ext = posixpath.splitext(fpath)
            if ext[1] == ".txt":
                parseOneInfoFile(fpath)

    
    # debug
    nodeList = sorted(list(node_data.keys()))
    for sname in nodeList:
        node_dict = node_data[sname]
        print(f"{sname}:")
        keyList = sorted(list(node_dict.keys()))
        for key in keyList:
            print(f"  {key} : {node_dict[key]}")

    makeCsvFile()
      


if __name__ == "__main__":
    main()

