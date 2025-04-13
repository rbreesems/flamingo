import argparse
import os
import re
import posixpath
from pathlib import Path
from dataclasses import dataclass

# Helper program for to parse serial log messages


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


version = "1.1"
infodir = "infofiles"
@dataclass
class LogEntry:

    tstamp: str
    txhost: str
    inmsg: str
    outmsg: str
    num_hops: int = 0
    

def parseOneLogFile(fpath, surface_node):
    global log_data
    global prefs_dict

    ifile = open(fpath,'r')
    lines = ifile.readlines()
    ifile.close()
    for line in lines:
        line = line.rstrip()
        line = filterColorCode(line)
        #print(line)
        if re.search(".*TextModule msg.*",line) or re.search(".*PhoneApi msg.*",line):
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

            hop_start = int(cwords[5].split('=')[1])
            hop_limit = int(cwords[4].split('=')[1])
            num_hops = hop_start - hop_limit
            entry = LogEntry(tstamp, txhost, inmsg, outmsg, num_hops)
            if host == surface_node:
                if re.search(".*PhoneApi msg:.*",line):
                    print(f"{entry.tstamp} \t\t\t\t\tOutgoing:  {entry.outmsg}")
            else:
                print(f"{entry.tstamp} Incoming:  {entry.inmsg} \t host: {entry.txhost}  numhops: {entry.num_hops}")


def main():
    
    global prefs_dict
    parser = argparse.ArgumentParser(description=f"Parse serial logs from cave testing, Version {version}.")
    parser.add_argument('logdir',type=str, help="Log directory containing log files, all files will parsed.")
    parser.add_argument('surface_node',type=str, help="Long name of surface node (outgoing messages).")

    args = parser.parse_args()
    
    if not posixpath.isdir(args.logdir):
         print("ERROR: first argument has to specify directory containing log files")
         return
    count = 0
    for entry in sorted(Path(args.logdir).iterdir(), key=os.path.getmtime):
        if entry.is_file():
            parseOneLogFile(posixpath.join(args.logdir,entry.name), args.surface_node)
            

    return

    

if __name__ == "__main__":
    main()

