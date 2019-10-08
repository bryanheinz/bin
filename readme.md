# bin
This repository is a collection of weird command line utilities that I've created.

## b64
b64 is used to encode or decode base64 strings.

```
Usage: b64 [option] [string]
    -e [string]
    -d [string]
```

## bat\_stat
bat\_stat is used to display information about a Macs battery and a _rough_ estimate on battery life.

`Usage: bat_stat [-v]`

## bt\_restart
bt\_restart is used to restart Bluetooth on macOS. bt\_restart uses the blueutil binary found [here](https://github.com/toy/blueutil).

`Usage: bt_restart`

## cf
cf is a script that will check your external IP and update the A record of a subdomain on Cloudflare with that IP. Update the script with your Cloudflare email, API key, domain, and subdomain.

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

## icp
icp takes an ICNS file and converts it to a PNG. icp will save the PNG to the same directory the ICNS file is in with the .png extension. If that directory isn't writable, icp will attempt to save it to your Desktop. You can also specify where to output the file using `-o /path/to/`.

```
This utility converts ICNS files to PNG.
Usage:   icp [icns path] [-f] [-o /path/to/]
Example: icp ~/Downloads/1Password.icns -f -o ~/Documents/icons/
Options:
	-f          Skips ICNS file check and forces the conversion to PNG.
	-o [path]   Specifies the output path to convert the icon to.
	-h		    Prints this help document.
```

## pf
pf is used to rename a script to postflight and make it executable. It's useful for updating a payload free package script.

`Usage: pf /path/to/script.py`

## pj
pj is used to print a json file in a readable format.

`Usage: pj [PATH]`

## prosign
prosign is a shortcut script to sign macOS configuration profiles. It requires you to have a developer account and you'll have to update the scripts dev\_ident variable with your developer certificate identity name that can be found in your Keychain.

prosign will output a signed profile to the same directory as the input profile with "-signed" appended to it.

```Usage: prosign [file path]
Example: prosign /Users/bryan/Desktop/com.company.app.mobileconfig```

## sb
sb is used to quickly and easily find booted Xcode simulators and clean up their status bar.

```
Usage: sb [--clear]
    --clear     resets status bar.
```

## write-speedtest
write-speedtest is used to get a rough estimate on the write speed to a target. It's useful for getting a feel of how fast a local disk is or a mounted share.

```
Usage: write-speedtest [options]
    --raw       prints the bytes per second
    --size  [n] file size in megabytes (default is 500MB)
    --path  [s] sets the path to test the disk speed
    --tests [n] how many test files to generate (default is 5)
```