import argparse
import subprocess
import time
import os
import re
import sys
import shlex
from datetime import datetime


# Helper program to check power status of nodes
# This program uses a node connected to USB serial
# to poll other nodes in the mesh for their power status


version = "1.0"
firmware_versions = (2.7, 3.0) # Low, high firmware limits (Major.Minor) for this version of the configurator
sleep_time = 20
range_test_extra_sleep = 20
infodir = "infofiles"
configdir = "configfiles"
max_retries = 3
default_power_file = "nodes_power.csv"

longname = ""
shortname = ""

nodeDb = {}
csvHeader =""

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
        args = shlex.split(cmd)
        output = runProgramCaptureOutput(args)

        # Detect the Meshtastic "multiple serial ports" condition and stop early.
        # This happens when multiple devices are attached and no --port is given.
        combined_err = (output.stderr or "") + "\n" + (output.stdout or "")
        if ("Multiple serial ports were detected" in combined_err
                and "--port" not in cmd):
            # Show the original Meshtastic warning (which includes the ports list)
            print("\nError from meshtastic -" + combined_err)
            # Provide a clear instruction for the user running this configurator.
            print(
                "\nERROR: Multiple Meshtastic devices were detected on serial ports.\n"
                "Please re-run this script and specify a single device using the '-p/--port' option.\n"
                "Example: python configure_node_2.7.py -p COM25 <settings.yml>"
            )
            sys.exit(1)

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


def main():

    parser = argparse.ArgumentParser(description=f"Utility for retrieving mesh nodes power status, Version {version}.\n This only works if the target node is known by the connected node.")
    parser.add_argument('-f', '--longname', dest='powerfile', type=str,
                        default=None,
                        help=f'path to power CSV file, default is {default_power_file}. All Node shortnames/ID must be in this file.\n The CSV header is Node id/ShortName/Battery/Voltage/Date. The contents of this file is updated by this script.')
    parser.add_argument('-n', '--nodes', dest='nodes', type=str,
                        default=None,
                        help='comma delimited list of nodes to check (shortnames). If unspecified, check all nodes in the power file')
    parser.add_argument('-p', '--port', dest='port', type=str,
                        default=None,
                        help='com port name of connected nod, optional, typically COMn')
    
    args = parser.parse_args()
    header = None

     # start config
    if args.port:
        meshcmd = f"meshtastic --port {args.port}"
    else:
        meshcmd = "meshtastic"

    defaultNodeList = []
    try:
        if args.powerfile:
            powerfile = args.powerfile
        else:
            powerfile = default_power_file
        with open(powerfile, 'r') as file:
            lines = file.readlines()
            header = lines[0].strip()
            
            for line in lines[1:]:
                line = line.strip()
                words = line.split(',')
                if len(words) < 2:
                    continue
                nodeId = words[0].strip()
                if len(nodeId) != 8:
                    nodeId = '0'  + nodeId
                shortName = words[1].strip()
                nodeDict = {}
                nodeDb[shortName] = nodeDict
                nodeDict['shortName'] = shortName
                defaultNodeList.append(shortName)
                nodeDict['nodeId'] = nodeId
                if len(words) > 2:
                    nodeDict['battery']  = words[2].strip()
                else:
                    nodeDict['battery']  = "N/A"
                if len(words) > 3:
                    nodeDict['voltage']  = words[3].strip()
                else:
                    nodeDict['voltage']  = "N/A"
                if len(words) > 4:
                    nodeDict['date']  = words[4].strip()
                else:
                    nodeDict['date']  = "N/A"
    except Exception as e:
        print(f"ERROR: Exiting, Failed to read powerfile: {powerfile}, {e}")
        exit(-1)
    print(f"Read powerfile: {powerfile}, found: {len(nodeDb)} nodes.")

    if args.nodes:
        nodeList = []
        for nodeName in args.nodes.split(','):
            nodeName = nodeName.strip()
            if nodeName not in nodeDb:
                print(f"Unable to find passed node name: {nodeName} in power file, skipping.")
            else:
                nodeList.append(nodeName)
    else:
        nodeList = defaultNodeList


    cd = datetime.now()
    dateString = f"{cd.year}-{cd.month}-{cd.day} {cd.hour}:{cd.minute}"
    for nodeName in nodeList:
        nodeDict = nodeDb[nodeName]
        nodeId = nodeDict['nodeId']
        powerquery = meshcmd + " --request-telemetry --dest " + nodeId
        device_info = runCmd(powerquery, echoOnly=False, silent=True )
        lines = device_info.splitlines()
        telemetryFound = False
        for line in lines:
            if re.match("^Aborting.*",line):
                print(f"Node {nodeName} did not respond, no data available.")
                break
            elif re.match("^Battery.*",line):
                words = line.split(':')
                nodeDict['battery'] = words[1].strip()
            elif re.match("^Voltage",line):
                words = line.split(':')
                nodeDict['voltage'] = words[1].strip()
            elif re.match("^Telemetry.*",line):
                telemetryFound = True
                words = line.split(':')
                nodeDict['date']  = dateString
                print(f"Found telemetry for {nodeName}")

        if telemetryFound:
            time.sleep(10)
 
    
    # write the results back out
    nodelist = list(nodeDb.keys())
    nodelist.sort()
    lines = []
    lines.append(f"{header}\n")
    for nodeName in nodelist:
        nodeDict = nodeDb[nodeName]
        lines.append(f"{nodeDict['nodeId']},{nodeName},{nodeDict['battery']},{nodeDict['voltage']},{nodeDict['date']}\n")

    #print(f"{lines}")
    with open(powerfile, 'w') as file:
        file.writelines(lines)

    print(f"File: {powerfile} updated.")
          
if __name__ == "__main__":
    main()




