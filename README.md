# bin
This repository is a collection of command line utilities that I've created.

## b64
b64 is used to encode or decode base64 strings.

```
Usage: b64 [option] [string]
    -e [string]
    -d [string]
```

## bat\_stat
bat\_stat is used to display information about a Macs battery and a _rough_ estimate on battery life.

`Usage: bat\_stat [-v]`

## cl
cl is used to open a URL in Chrome without Chrome's user interface.

`Usage: cl [URL]`

## fire-proxy
fire-proxy is used to enable or disable Firefox's proxy. It sets Firefox's proxy to 127.0.0.1 with the port 4020. I use this in conjunction with an SSH reverse proxy tunnel (`ssh -D 4020 user@host`).

```
Usage: fire-proxy [option]
	--status to check if Firefox's proxy is enabled or not
	--on     to enable Firefox's proxy (requires Firefox restart)
	--off    to disable Firefox's proxy (requires Firefox restart)
```

## get\_macos\_installer\_version
get\_macos\_installer\_version is used to pull what version of macOS the installer will install. It's useful for when you have a macOS installer that you forgot to label with the version number.

`Usage: get_macos_installer_version [PATH]`

## host-check
host-check is used to watch a host's port. It's useful when rebooting a server or service and you want to watch for a specific port to become available again. host-check **requires** nmap.

```
Usage: host-check --port 22 --ip 127.0.0.1 --delay 30
    --port  [n]   specifies the port (e.g. 22)
    --ip    [IP]  specifies the IP address (e.g. 127.0.0.1)
    --dns   [DNS] specifies the DNS name (e.g. google.com)
    --delay [n]   specifies the seconds between each check
```

## pf
pf is used to rename a script to postflight and make it executable. It's useful for updating a payload free package script.

`Usage: pf /path/to/script.py`

## pj
pj is used to print a json file in a readable format.

`Usage: pj [PATH]`

## write-speedtest
write-speedtest is used to get a rough estimate on the write speed to a target. It's useful for getting a feel of how fast a local disk is or a mounted share.

```
Usage: write-speedtest [options]
    --raw       prints the bytes per second
    --size  [n] file size in megabytes (default is 500MB)
    --path  [s] sets the path to test the disk speed
    --tests [n] how many test files to generate (default is 5)
```