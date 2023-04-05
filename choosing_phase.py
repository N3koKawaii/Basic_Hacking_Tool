#!/usr/bin/env python

import subprocess
import ipaddress
import threading
import time

import hacking_phase
import arp_spoof


class Choosing_Phase:
    def __init__(self):
        self.continue_start = True
        self.MENU_OPTIONS = {
            "Start Hacking": self.start_hacking,
            "Device Scanning": self.device_scanning,
            "Network Interface": self.set_network_interface,
            "Target Ip": self.set_target_ip,
            "Help": self.help,
            "Exit": self.close_program
        }
        self.interface = subprocess.check_output('ip r | cut -d " " -f5', shell=True).decode().split("\n")[0]
        self.your_ip = subprocess.check_output(f'ifconfig {self.interface} | grep broadcast | cut -d " " -f10',
                                               shell=True).decode().strip()
        self.gateway = \
            subprocess.check_output(f'ip r | grep {self.interface} | cut -d " " -f3', shell=True).decode().split("\n")[
                0]
        self.target_ip = ""
        self.ip_range = subprocess.check_output(f'ip r | grep {self.interface} | cut -d " " -f1', shell=True).decode().split("\n")[1]
        arp_spoof.restoring_ip(self.target_ip, self.gateway, self.interface)

    def start_hacking(self):
        if self.target_ip == "":
            print("\n[-] Target ip has not been setting up\n")
        else:
            self.continue_start = False
            bg_thread = threading.Thread(target=arp_spoof.run, args=(self.target_ip, self.gateway, self.interface))
            bg_thread.start()
            time.sleep(2)

            hacking_phase.Hacking_Phase(self.target_ip, self.gateway, self.your_ip, self.interface)

    def device_scanning(self):
        print(f"[+] This may take some time...\n[+] Scanning devices....")
        result = subprocess.check_output(f'nbtscan -r {self.ip_range}', shell=True).decode()
        print(result)

    def set_network_interface(self):
        while True:
            self.interface = input("[+] Enter the IP (E.g. wlan0) : ")
            all_interface = subprocess.check_output("ifconfig", shell=True).decode()
            if self.interface in all_interface:
                self.your_ip = subprocess.check_output(f'ifconfig {self.interface} | grep broadcast | cut -d " " -f10',
                                                       shell=True).decode().strip()
                self.gateway = \
                    subprocess.check_output(f'ip r | grep {self.interface} | cut -d " " -f3',
                                            shell=True).decode().split(
                        "\n")[0]
                self.ip_range = \
                    subprocess.check_output(f'ip r | grep {self.interface} | cut -d " " -f1',
                                            shell=True).decode().split(
                        "\n")[1]

                self.target_ip = ""
                print("[+] Interface has been updated.\n")
                break
            else:
                print("\n[-] Interface cannot be found.\n")
                print(f"[+] Here is your interfaces...\n\n{all_interface}")

    def set_target_ip(self):
        self.target_ip = input("[+] Enter the IP (E.g. 192.168.18.23) : ")
        try:
            ipaddress.ip_address(self.target_ip)
            print("[+] IP address has been updated.\n")
            if self.target_ip not in subprocess.check_output(f'nbtscan -r {self.ip_range}', shell=True).decode():
                print("\n[-] IP address not found\n")
                self.set_target_ip()
        except ValueError:
            print("\n[-] Invalid IP address.\n")
            self.set_target_ip()

    def help(self):
        print("\nStarting Options\n")
        print("Type the name to use the function. E.g. 'start hacking'")
        print("-------------------------------------")
        for key, value in self.MENU_OPTIONS.items():
            if key == "Device Scanning":
                print(f"  * {key} (DO THIS BEFORE SETTING TARGET IP)")
            elif key == "Network Interface":
                print(f"  * {key} (DEFAULT 'eth0')")
            else:
                print(f"  * {key}")
        print("-------------------------------------\n")

    def close_program(self):
        print("\n\n[+] Goodbye <3")
        time.sleep(1)
        print("[+] System Closing...")
        arp_spoof.restoring_ip(self.target_ip, self.gateway, self.interface)

        time.sleep(1)
        exit(0)

    def main(self):
        print("\n\n------------------ Basic Hacking Tool ------------------\n\n")
        print("[+] Type 'help' to know how to use this tool.\n")

        while self.continue_start:
            print(
                f"Interface : {self.interface}\nYour IP   : {self.your_ip}\nGateway   : {self.gateway}\nTarget IP : {self.target_ip}\n\n")

            try:
                user_input = input("--> ")
                user_input = user_input.title()

                try:
                    self.MENU_OPTIONS[user_input]()
                except KeyError:
                    print("\n[-] Error input.\n")
            except KeyboardInterrupt:
                self.close_program()
