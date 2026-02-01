
import argparse
import os
import re
import yaml
import sys
import posixpath

# Helper program for to consolidate information from node info txt files 
# into one csv file

version = "1.1"
infodir = "infofiles"

columns_name_dict = {}  # key is column_name, value is column_data_key
column_list = []  # list of column names

node_data = {}  # key is short name, value is data dict that maps column_data_key to column_name

prefs_dict = {} # parsed from yaml file

keys_dict = {}

# To print CSV data:
# for each node:
#   get data dict
#   for each colum_name
#      get column_data_key, retrieve value from data dict
# Known values:
#- "Short Name"
#  - "MacID"
#  - "Long Name"
#  - "HW Model"
# - "FW Ver"
#  - "Role"
#  - "hasWifi"

def parseOneInfoFile(fpath):
    global node_data
    global prefs_dict
    global keys_dict

    node_dict = {}
    print(f"Parsing infofile: {fpath}")
    ifile = open(fpath,'r')
    lines = ifile.readlines()
    ifile.close()
    metaKeys = set(["firmwareVersion", "hwModel", "hasWifi", "role"])
    state = "init"
    for line in lines:
        line = line.rstrip('\n')
        if re.match("^Nodes in mesh:.*",line):
            state = "mesh"
            continue
        if re.match("^Preferences:.*",line):
            state = "prefs"
            continue
        if state == "init":
            if re.match("^Owner:.*", line):
                # parse long,short names
                newline = line.replace("Owner: ","")
                nwords = newline.split('(',1)
                node_dict["global_Long Name"] = nwords[0]
                if len(nwords) == 2:
                    node_dict["global_Short Name"] = nwords[1].replace(')','')
                continue
            if re.match("^My info:.*", line):
                # need to parse myNodeNum in order to extract MAC later
                words = line.split()
                i = 0
                for word in words:
                    if word == "\"myNodeNum\":":
                        id = int(words[i+1].replace(',',''))
                        node_dict["myNodeNum"] = words[i+1]
                        if str(id) in keys_dict:
                            node_dict['global_keyStored'] = 'yes'
                        else:
                            node_dict['global_keyStored'] = 'no'
                        break
                    i += 1
            if re.match("^Metadata:.*", line):
                # parse
                #  - "HW Model"
                # - "FW Ver"
                #  - "Role"
                #  - "hasWifi"
                words = line.split()
                i = 0
                for word in words:
                    if ':' in word:
                        word = word.replace('"','')
                        word = word.replace(':','')
                    if word in metaKeys:
                        node_dict[f"global_{word}"] = words[i+1].replace(',','')
                    i += 1
        
        if state == "mesh":
            nodeNum = node_dict.get("myNodeNum",None)
            if nodeNum is None:
                continue
            words = line.split(':',1)
            if len(words) == 2:
                key = words[0].strip()
                key = key.replace('"','')
                v = words[1].strip()
                if key == "num" and v == nodeNum:
                    state = "mac"
                    continue
        if state == "mac":
            words = line.split(':',1)
            if len(words) == 2:
                key = words[0].strip()
                key = key.replace('"','')
                if key == "macaddr":
                    v = words[1].strip()
                    v = words[1].replace(',','')
                    v = v.replace('"','')
                    mwords = v.split(":")
                    mac = mwords[len(mwords)-2]+mwords[len(mwords)-1]
                    node_dict["global_macaddr"] = mac
                    node_dict["global_id"] = "%x" % (int(nodeNum.replace(',','')))
                    state = "null"
                    continue
        if state == "prefs":
            if line.strip() == "}":
                current_pdict = None
                continue
            words = line.split(':',1)
            if len(words) != 2:
                continue
            v = words[1].strip()
            v = v.replace(',','')
            k = words[0].replace('"','')
            k = k.strip()
            if v == "{":
                current_dict_name = k
                current_pdict = prefs_dict.get(k, None)
                continue
            if current_pdict and k in current_pdict:
                # found a value
                node_dict[f"{current_dict_name}_{k}"] = v
                continue
    
    if "global_Short Name" in node_dict:
        node_data[node_dict["global_Short Name"]] = node_dict
    return 


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

def readAllKeysFromFile(fname):
    """
    Read keys from keys.txt, 
    Returns nested dict with private_key, public_key, config_file, or None if not found
    Top-level dict is nodeId.
    Always returns a dict
    """
    keys_file = fname
    
    if not os.path.exists(keys_file):
        return {}
    

    try:
        topDict = {}
        with open(keys_file, 'r') as f:
            first_line = True
            for line in f:
                line = line.strip()
                # Skip header line
                if first_line and line == "nodeId,private_key,public_key,config_file":
                    first_line = False
                    continue
                if line and not line.startswith('#'):
                    # Format: nodeId,private_key,public_key,config_file
                    parts = line.split(',', 3)
                    if len(parts) == 4:
                        id = parts[0].replace('!','')
                        id = int(id,16) # convert to decimal
                        topDict[str(id)] = {
                                'private_key': parts[1].strip(),
                                'public_key': parts[2].strip(),
                                'config_file': parts[3].strip()
                            }
                first_line = False
    except Exception as e:
        print(f"ERROR: Failed to read keys.txt: {e}")

    return topDict


def main():
    global columns_name_dict
    global column_list
    global prefs_dict
    global keys_dict
    parser = argparse.ArgumentParser(description=f"Generate CSV file for cave nodes, Version {version}.")
    parser.add_argument('configFile',type=str, help="YAML file containing configuration specifying what is to be included, required.")
    parser.add_argument('-kf', '--keysFile', dest='keysFile', type=str,
                        default='keys.txt',
                        help="file containing public/private keys, default is keys.txt.")

    
    args = parser.parse_args()

    keys_dict = readAllKeysFromFile(args.keysFile)
   
    try:
        with open(args.configFile, 'r') as file:
            yml_opts = yaml.safe_load(file) # Use safe_load to prevent arbitrary code execution
    except Exception as e:
        print("ERROR: Unexpected error parsing yml file: %s, %s/%s" % (args.configFile, sys.exc_info()[0], e))
        exit(-1)

    fixed_cols = yml_opts.get('fixed_cols',None)
    if fixed_cols is None:
        print(f"ERROR, expecting 'fixed_cols' dict that has list of fixed columns in file: {args.configFile}, exiting.")
        return -1
    

    addColumn("global_keyStored", "keyStored")    # for keys file entry
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

