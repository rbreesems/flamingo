#!/usr/bin/env python3
"""
Extract keys from info files in a directory and write them to keys.txt.
This script parses all .txt files in the specified directory (default: infofiles)
and extracts nodeId, private key, and public key from each, writing them to keys.txt.


# Usage:
Run from utils/configurator/

This is to be run once, targeting the folder that has your info files, and will create a keys.txt file. 
The files are parsed from oldest modified, so the most recent key should be retained.

It should be able to be run multiple times, but as 'last updated' is not retained, an old log will take precedence over an existing entry in keys.txt.

"""

import os
import sys
import json
import yaml
import argparse
import glob

def extractKeysFromInfoFile(info_content):
    """
    Extract nodeId, private key, and public key from device info file content.
    Returns dict with nodeId, private_key, public_key, or None if extraction fails.
    nodeId is in hex format with ! prefix (e.g., "!710c5ed7")
    """
    nodeId = None
    public_key = None
    private_key = None
    
    # Extract nodeId from "My info" line - convert myNodeNum to hex with ! prefix
    for line in info_content.splitlines():
        if line.startswith("My info"):
            try:
                json_str = line.split(':', maxsplit=1)[-1].strip()
                my_info = json.loads(json_str)
                myNodeNum = my_info.get('myNodeNum')
                if myNodeNum:
                    # Convert to hex and add ! prefix
                    nodeId = f"!{myNodeNum:08x}"
            except Exception as e:
                print(f"ERROR: Failed to parse My info line: {e}")
                return None
    
    # Extract keys from "security" section
    lines = info_content.splitlines()
    security_lines = []
    in_security = False
    bcount = 0
    
    for line in lines:
        if '"security":' in line or '"security" :' in line:
            security_lines.append(line)
            in_security = True
            bcount = 1
            continue
        if in_security:
            security_lines.append(line)
            if '{' in line:
                bcount += line.count('{')
            if '}' in line:
                bcount -= line.count('}')
            if bcount == 0:
                break
    
    if len(security_lines) > 0:
        try:
            security_text = '\n'.join(security_lines)
            # Remove everything before the first '{'
            # brace_idx = security_text.find('{')
            # if brace_idx != -1:
            #     security_text = security_text[brace_idx:]
            # For all lines in security_lines, strip starting white space

            # security_text = [line.lstrip() for line in security_text]
            security_text = security_text.rstrip(',')
            print("---")
            print(security_text)
            print("---")
            security_data = yaml.safe_load(security_text)
            security_dict = security_data.get('security', {})
            public_key = security_dict.get('publicKey')
            private_key = security_dict.get('privateKey')
        except Exception as e:
            print(f"WARNING: Failed to parse security section: {e}")
    
    if nodeId and public_key and private_key:
        return {
            'nodeId': nodeId,
            'public_key': public_key,
            'private_key': private_key
        }
    else:
        return None

def writeKeysToFile(nodeId, private_key, public_key, config_file, keys_file="keys.txt"):
    """
    Write or update keys entry in keys.txt file.
    If entry with same nodeId exists, replace it. Otherwise append.
    Format: nodeId,private_key,public_key,config_file
    """
    entries = []
    header = "nodeId,private_key,public_key,config_file"
    has_header = False
    
    # Read existing entries
    if os.path.exists(keys_file):
        try:
            with open(keys_file, 'r') as f:
                first_line = True
                for line in f:
                    line = line.strip()
                    if first_line and line == header:
                        has_header = True
                        first_line = False
                        continue
                    if line and not line.startswith('#'):
                        # Format: nodeId,private_key,public_key,config_file
                        parts = line.split(',', 3)
                        if len(parts) == 4:
                            existing_nodeId = parts[0].strip()
                            # Skip if this is the nodeId we're updating
                            if existing_nodeId != nodeId:
                                entries.append(line)
                    first_line = False
        except Exception as e:
            print(f"WARNING: Error reading {keys_file}: {e}")
    
    # Add or update entry
    new_entry = f"{nodeId},{private_key},{public_key},{config_file}"
    entries.append(new_entry)
    
    # Write back to file
    try:
        with open(keys_file, 'w') as f:
            f.write(header + '\n')
            for entry in entries:
                f.write(entry + '\n')
        return True
    except Exception as e:
        print(f"ERROR: Failed to write {keys_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Extract keys from info files and write to keys.txt")
    parser.add_argument('-d', '--directory', dest='directory', type=str,
                        default='infofiles',
                        help='Directory containing info files (default: infofiles)')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        default='keys.txt',
                        help='Output keys file (default: keys.txt)')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"ERROR: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    # Find all .txt files in the directory
    pattern = os.path.join(args.directory, "*.txt")
    info_files = glob.glob(pattern)
    # Sort by modification time, oldest first
    info_files.sort(key=lambda f: os.path.getmtime(f))
    
    if not info_files:
        print(f"No .txt files found in {args.directory}")
        sys.exit(0)
    
    print(f"Processing {len(info_files)} info file(s) from {args.directory}...")
    
    processed = 0
    failed = 0
    
    for info_file in info_files:
        try:
            with open(info_file, 'r', encoding='utf-8', errors='ignore') as f:
                info_content = f.read()
            
            keys_info = extractKeysFromInfoFile(info_content)
            if keys_info:
                # Use the info filename as the config_file identifier (since we don't know the actual config)
                config_file = f"from_info_file:{os.path.basename(info_file)}"
                if writeKeysToFile(keys_info['nodeId'], keys_info['private_key'], 
                                 keys_info['public_key'], config_file, args.output):
                    print(f"  ✓ Extracted keys from {os.path.basename(info_file)} (nodeId: {keys_info['nodeId']})")
                    processed += 1
                else:
                    print(f"  ✗ Failed to write keys for {os.path.basename(info_file)}")
                    failed += 1
            else:
                print(f"  ✗ Failed to extract keys from {os.path.basename(info_file)}")
                failed += 1
        except Exception as e:
            print(f"  ✗ Error processing {os.path.basename(info_file)}: {e}")
            failed += 1
    
    print(f"\nCompleted: {processed} file(s) processed successfully, {failed} failed")
    print(f"Keys written to {args.output}")

if __name__ == "__main__":
    main()
