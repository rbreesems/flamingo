import argparse
import os
import re
import posixpath
import yaml
import sys
from pathlib import Path
from dataclasses import dataclass
import emoji

# Helper program for to parse serial log messages
# This parsing compatible with greater than HCRU 7/25.2 that
# fixed problem with logging of long messages

def makeEmojiDict():

    all_emojis = emoji.EMOJI_DATA

    emoji_byte_dict = {}  # maps byte string to english string
    # Print the first 10 emojis and their English short names
    for i, (char, data) in enumerate(all_emojis.items()):
        utf_bytes = char.encode('utf-8')
        if len(utf_bytes) > 4:
            continue
        if utf_bytes[0] == 0xf0:
            s = f"{utf_bytes[1:]}"
        else:
            s = f"{utf_bytes}"
        s = s.replace('\\x','')
        s = s[2:]
        s = s.replace("\'","")
        key = ':' + s + ':'
        emoji_byte_dict[key] = data['en'] 
        #print(f"key: {key}, {char} : {data['en']}")

    return emoji_byte_dict
        


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


version = "1.2"
infodir = "infofiles"
@dataclass
class LogEntry:

    tstamp: str
    txhost: str
    inmsg: str
    outmsg: str
    num_hops: int = 0
    
def isOutgoing(host, yml_opts):
    outgoing = yml_opts.get('outgoing',None)
    if outgoing is None:
        return False
    new_host = outgoing.get(host, None)
    if new_host is None:
        return False
    return True
    
def getOutgoingName(host, yml_opts):
    outgoing = yml_opts.get('outgoing',None)
    if outgoing is None:
        return host
    return outgoing.get(host, None)

def getIncomingName(host, yml_opts):
    incoming = yml_opts.get('incoming',None)
    if incoming is None:
        return host
    new_host = incoming.get(host, None)
    if new_host is None:
        return host
    return new_host

def translate_host(host, yml_opts):

    new_host = getOutgoingName(host, yml_opts)
    if new_host is not None:
        return 
    
def replaceEmoji(msg, emoji_byte_dict):
    if not (':' in msg):
        return msg
    elist = re.findall(":[0-9a-f]{6}:", msg)
    for emo in elist:
        msg = msg.replace(emo, emoji_byte_dict.get(emo,""))
    return emoji.emojize(msg)

def parseOneLogFile(fpath, yml_opts, emoji_byte_dict, ofile):
    global log_data
    global prefs_dict

    
    ifile = open(fpath,'r')
    lines = ifile.readlines()
    ifile.close()
    state = 'default'
    for line in lines:
        line = line.rstrip()
        line = filterColorCode(line)
        #print(line)
        if state == 'default':
            if 'Routing sniffing' in line:
                continue
            if re.search(".*TextModule msg.*",line):
                
                words = line.split()
                tstamp = words[2]
                cwords = line.split(',')
                if len(cwords) < 2:
                    continue
                host = ""
                for word in cwords:
                    if 'ln=' in word:
                        host = cwords[2].split('=')[1]
                        break
                msg = ""
                txhost = ""
                if not isOutgoing(host, yml_opts):
                    txhost = getIncomingName(host, yml_opts)
                if len(cwords) < 6:
                    print(f"DEBUG: {line} ")
                    cwords  = cwords
                try:
                    hop_limit = 0
                    hop_start = 0
                    for word in cwords:
                        if 'hop_start=' in word:
                            hop_start = int(word.split('=')[1])
                        if 'hop_limit=' in word:
                            hop_limit = int(word.split('=')[1])
                    num_hops = hop_start - hop_limit
                    state = 'message'
                except Exception as e:
                    print(cwords)
                    print(f"ERROR: {line}, exception {e} ")
                    
                
                continue
        if state == 'message':
            if re.match(".*z=.*",line):
                msg = msg+line.split("z=",1)[1]
                continue
            elif msg != "":
                msg = replaceEmoji(msg,emoji_byte_dict)
                state = 'default'
                if isOutgoing(host, yml_opts):
                    if re.match("^#.*", msg) or re.match("^P#.*", msg) or re.match("^`#.*", msg):
                        continue
                    
                    entry = LogEntry(tstamp, txhost, "", msg, num_hops)
                    s = f"{entry.tstamp} \t\t\t\t\tOutgoing ({getOutgoingName(host, yml_opts)}):  {entry.outmsg}"
                    if ofile:
                        ofile.write(f"{s}\n")
                    else:
                        print(s)
                else:
                    txhost = getIncomingName(host, yml_opts)
                    entry = LogEntry(tstamp, txhost, msg, "", num_hops)
                    s = f"{entry.tstamp} Incoming:  {entry.inmsg} \t host: {entry.txhost}  numhops: {entry.num_hops}"
                    if ofile:
                        ofile.write(f"{s}\n")
                    else:
                        print(s)
            else:
                state = 'default'
    if ofile:
        ofile.close()

def main():
    
    global prefs_dict
    parser = argparse.ArgumentParser(description=f"Parse serial logs from cave testing, Version {version}.")
    parser.add_argument('argumentsFile',type=str, help="YAML file containing all arguments.")
    parser.add_argument('-o', '--outFile', dest='outFile', type=str,
                        default=None,
                        help="optional output file for parsed output, will be in UTF-8 encoding.")
    args = parser.parse_args()

    try:
        with open(args.argumentsFile, 'r') as file:
            yml_opts = yaml.safe_load(file) # Use safe_load to prevent arbitrary code execution
    except Exception as e:
        print("ERROR: Unexpected error parsing yml file: %s, %s/%s" % (args.argumentsFile, sys.exc_info()[0], e))
        exit(-1)
    logdir = yml_opts.get('logdir',None)
    if logdir is None:
         print("ERROR: Expecting 'logdir' value in yml arguments file")
         return
    
    if not posixpath.isdir(logdir):
         print(f"ERROR: value for 'logdir' of {logdir} is not a directory ")
         return
    
    ofile = None
    if args.outFile:
        try:
            ofile = open(args.outFile, 'w', encoding="utf-8")
        except Exception as e:
            print("ERROR: Unexpected error opening output file: %s, %s/%s" % (args.outFile, sys.exc_info()[0], e))
            exit(-1)
    
    emoji_byte_dict = makeEmojiDict()
    for entry in sorted(Path(logdir).iterdir(), key=os.path.getmtime):
        if entry.is_file():
            parseOneLogFile(posixpath.join(logdir,entry.name), yml_opts, emoji_byte_dict, ofile)
            

    return

    

if __name__ == "__main__":
    main()

