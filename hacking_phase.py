#!/usr/bin/env python

import subprocess

import choosing_phase
import port_scanning
import dns_spoof
import packet_sniffer


class Hacking_Phase:
    def __init__(self, target_ip, gateway, your_ip, interface):
        self.modules_options = {
            "ping": {
                "description": "Show if you can reach host and how long will it takes",
                "function": self.ping
            },
            "pscan": {
                "description": "Port Scanning",
                "function": self.port_scanning
            },
            "sniff": {
                "description": "Sniffing data of what target acts",
                "function": self.packet_sniffing
            },
            "dnsspoof": {
                "description": "Redirect http web pages into a specific web page",
                "function": self.dns_spoof
            },
            "help": {
                "description": "Show all the available modules",
                "function": self.show_modules
            },
            "back": {
                "description": "Back to home page",
                "function": self.back
            },
        }
        self.target_ip = target_ip
        self.gateway = gateway
        self.your_ip = your_ip
        self.interface = interface
        self.continue_hacking = True
        self.main()

    def ping(self):
        print("[+] This may take a few seconds...")
        try:
            ping_result = subprocess.check_output(f"ping -c 4 {self.target_ip}", shell=True).decode()
            print("\n\n---------------- Ping Result ----------------\n\n")
            print(ping_result)
        except subprocess.CalledProcessError:
            print("\n[-] Could not ping the target\n")

    def port_scanning(self):
        print("-" * 70)
        methods = "\n\t1. Normal \t : Scanning which ports are opening\n" \
                  "\t2. Slow \t : Scanning opening ports and the softwares\n" \
                  "\t3. Specific Port : Scanning the port for more details\n"
        print(methods)
        print("-" * 70)

        try:
            choice = int(input("\nChoose the method you want : "))
            if choice == 1:
                port_scanning.port_scanning_fast(self.target_ip)
            elif choice == 2:
                port_scanning.port_scanning_slow(self.target_ip)
            elif choice == 3:
                port = input("\nEnter the port : ")
                if "0" <= port <= "65535" and port.isnumeric():
                    port_scanning.port_scanning_specific(self.target_ip, port)
                else:
                    print("\n[-] Invalid input...\n")
                    self.port_scanning()
            else:
                print("\n[-] Invalid input...\n")
                self.port_scanning()
        except ValueError:
            print("\n[-] Invalid input...\n")
            self.port_scanning()

    def packet_sniffing(self):
        try:
            packet_sniffer.sniff(self.interface)
        except KeyboardInterrupt:
            print("[+] Stopping sniffing")

    def dns_spoof(self):
        subprocess.call("service apache2 restart", shell=True)
        dspoof = dns_spoof.DNS_SPOOF(self.your_ip)
        try:
            dspoof.run()
        except KeyboardInterrupt:
            dspoof.stop()

    def show_modules(self):
        print("\nAvailable Modules\n")
        print("Type the name to use the module. E.g. 'pscan'")
        print("-" * 70)
        for key, value in self.modules_options.items():
            print('    {:<12}:  {}'.format(key, value['description']))
        print("-" * 70 + "\n")

    def back(self):
        choosing_phase.Choosing_Phase().main()

    def main(self):
        print("\n\n------------------ Hacking Module Selection ------------------\n\n")
        print("[+] Type 'help' to show all the modules.\n")

        while self.continue_hacking:
            try:
                user_input = input("--> ")
                user_input = user_input.lower()

                try:
                    self.modules_options[user_input]["function"]()
                except KeyError:
                    print("\n[-] Module not found...\n")
            except KeyboardInterrupt:
                choosing_phase.Choosing_Phase().close_program()
