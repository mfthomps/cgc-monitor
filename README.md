# cgc-monitor
Cyber Grand Challenge forensics harness and automated analysis based on Simics
The CGC Monitor provides two primary functions: 1)forensic analysis for purposes of vetting software submissions; 
and, 2) automated support for analysis of CGC binaries via an Ida Pro gdb client.  Both functions rely on the Simics full system 
emulator.

The CGC Monitor lacks complete documentation, though the basic chain of scripts and dependencies can be derived by starting with:
zk/monitorUtils/cgc-monitor.md to  understand the forensic vetting function used in CFE; and with
idaClient/README_IDA_CLIENT.md for the analyst functions.  

A brief summary of the high level directories follows:

idaClient -- scripts used on a client computer to interact with a CGC Monitor
simics/monitorCore -- the primary Simics scripts that provide monitoring of software
simics/simicsScripts -- utilties to start the monitor and manage the monitor, including ts disk image files
simics/ida -- Ida Python scripts used by the Ida Pro client.
simics/slaveInstall -- utilities to help manage provisioning of a CGC Monitor slave
zk -- utilities and services required by the monitor, including software that runs on emulated infrastructure
game_notify -- interacts with CGC game infrastructure to obtain data to be vetted.
scoreUtils -- utilities for analysis of CFE artifacts