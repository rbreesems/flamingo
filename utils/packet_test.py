import argparse
import os
import re
import yaml
import sys
import posixpath
import time
import subprocess


# Program that sends automatic packets and checks ack back
#


version = "1.0"
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

def runCmd(cmd, echoOnly=False, silent=False, reboot=False, sleep_time=20):

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
    
def main():
    
    parser = argparse.ArgumentParser(description=f"Send automated packets, record success rat, Version {version}.")
    parser.add_argument('-i','--id',type=str, help="target node id", default=None)
    parser.add_argument('-c', '--count',type=int, help="packet count", default=1)
    parser.add_argument('-m', '--msg',type=str, help="msg to send", default="Hello from packet test")
    parser.add_argument('-d', '--delay',type=int, help="delay in seconds between packets", default=15)
    parser.add_argument('-s', '--silent',action='store_true',help="", default=False)

    args = parser.parse_args()
    delay = args.delay
    count = args.count

    success_count = 0
    packet_count = 0
    while (packet_count < count):
        cmdargs = ['meshtastic',
               '--sendtext',
               args.msg,
               '--dest',
                args.id
               ]
        packet_count += 1
        print(f"Sending packet: {packet_count}")
        output = runProgramCaptureOutput(cmdargs)
        lines = output.stdout.split('\n')
        for line in lines:
            print(line)
            if 'received an ack' in line.lower():
                success_count += 1
        print(f"Success rate is {success_count}/{packet_count}")
        time.sleep(delay)


if __name__ == "__main__":
    main()

    

