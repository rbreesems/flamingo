import argparse
import os
import re
import yaml
import sys
import posixpath
import time
import random
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
    
    parser = argparse.ArgumentParser(description=f"Send automated packets, either bcast or direct (if direct, record success rate), Version {version}.")
    parser.add_argument('-i','--id',type=str, help="target node id", default=None)
    parser.add_argument('-c', '--count',type=int, help="packet count", default=1)
    parser.add_argument('-b', '--bcast',action='store_true',help="if used, send bcast message, no ack check", default=False)
    parser.add_argument('-m', '--msg',type=str, help="msg to send", default="Hello from packet test")
    parser.add_argument('-d', '--delay',type=int, help="delay in seconds between packets", default=20)
    parser.add_argument('-s', '--silent',action='store_true',help="", default=False)
    parser.add_argument('-p', '--port',type=str,help="port number", default='')

    args = parser.parse_args()
    delay = args.delay
    delay = random.randint(delay-delay/2,delay+delay/2)
    count = args.count

    success_count = 0
    packet_count = 0
    while (packet_count < count):
        cmdargs = ['meshtastic',
               '--sendtext',
               f"#{packet_count}: {args.msg}",
                ]
        if args.bcast:
                cmdargs.append('--ch-index')
                cmdargs.append('0')
        else:
                cmdargs.append('--dest')
                cmdargs.append(args.id)
                cmdargs.append('--ack')
        if args.port != '':
            cmdargs.append('--port')
            cmdargs.append(args.port)
        packet_count += 1
        print(f"Sending packet: {packet_count}")
        output = runProgramCaptureOutput(cmdargs)
        lines = output.stdout.split('\n')
        for line in lines:
            print(line)
            if not args.bcast:
                if 'received an ack' in line.lower():
                    success_count += 1
                elif 'received an nak' in line.lower():
                    continue
        
        if not args.bcast:
            print(f"Success rate is {success_count}/{packet_count}")
        time.sleep(delay)
    print(f"Finished sending {packet_count} packets")



if __name__ == "__main__":
    main()

    

