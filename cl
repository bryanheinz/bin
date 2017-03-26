#!/usr/bin/python
import subprocess
from sys import argv

def help():
    print("")
    print("cl opens the specified URL in Chrome without Chrome's interface.")
    print("Usage: chromeless http[s]://url")
    print("Defaults to https:// if http:// isn't specified.")
    print("")
    exit(0)

try:
    script, url = argv
except:
    help()
    
if "-h" in url or '--help' in url:
    help()

if "http" not in url:
    url = 'https://' + url
    
cmd = ['open', '-na', 'Google Chrome', '--args', '--app={0}'.format(url)]
subprocess.call(cmd)