#!/usr/bin/env python
# coding:utf-8

import nmap


nm = nmap.PortScanner()  
nm.scan('61.139.105.107', '20-443')

#print nm.command_line()
#print nm['115.239.210.26'].all_protocols()

for host in nm.all_hosts():
    print host
    for proto in nm[host].all_protocols():
        # get protocols all port
        lport = nm[host][proto].keys()
        print lport
        lport.sort()
        for port in lport:
            print ('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))