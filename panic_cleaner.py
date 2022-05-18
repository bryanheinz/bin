#!/usr/bin/env python3

"""
This script parses macOS kernel panic logs and attempts to clean up and shorted
them to be a little more readable.
"""

import json
import pathlib
import argparse

def value_converter(dv):
    if isinstance(dv, dict):
        return convert_nested_dict(dv)
    elif isinstance(dv, str):
        if dv.startswith('{'):
            return json.loads(dv)
    return dv

def convert_nested_dict(dict_data):
    new_dict = {}
    for dkey, dvalue in dict_data.items():
        new_dict[dkey] = value_converter(dvalue)
    return new_dict

parser = argparse.ArgumentParser()
parser.add_argument('dir', help="Path to panic log to parse.")
args = parser.parse_args()

panic_log = pathlib.Path(args.dir)
panic_log_dir = panic_log.parent
panic_log_cleaned = panic_log_dir / f"CLEAN-{panic_log.name}"

with open(panic_log, 'r', encoding='utf-8') as fp:
    file_lines = fp.readlines()

panic_meta = file_lines[0]
panic_data = file_lines[1:]
panic_data_str = '\n'.join(panic_data)
data = json.loads(panic_data_str)
expanded_data = value_converter(data)

skip_keys = ['binaryImages', 'processByPid']
with open(panic_log_cleaned, 'w', encoding='utf-8') as fp:
    
    for key, value in expanded_data.items():
        if key in skip_keys: continue
        if isinstance(value, dict):
            fp.write(f"{key}: ")
            fp.write(json.dumps(value, indent=4))
        else:
            fp.write(f"{key}: {value}")
        fp.write("\n\n")

print("Saved clean file to:")
print(f"\t{panic_log_cleaned}")
