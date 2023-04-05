#!/usr/bin/env python

import socket
import subprocess


def port_scanning_fast(target_ip):
    print(f"[+] Scanning Port of {target_ip}....\n")
    for port in range(1, 65535):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        is_close = s.connect_ex((target_ip, port))

        if not is_close:
            print(f"Port {port} is open")
        s.close()


def port_scanning_slow(target_ip):
    print(f"[+] This will take up to 2 minutes to process.\n[+] Scanning Port of {target_ip}....\n")
    result = subprocess.check_output(f'nmap -T4 -sV -p0-65535 {target_ip}', shell=True).decode()
    print(result)


def port_scanning_specific(target_ip, port):
    print(f"[+] Scanning Port {port} of {target_ip}....\n")
    result = subprocess.check_output(f'nmap -T4 -p {port} -sV --script=vuln {target_ip}', shell=True).decode()
    print(result)
