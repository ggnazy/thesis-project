from scapy.all import *
import argparse
import logging
from datetime import datetime

class NetworkAnalyzer:
    def __init__(self, interface, target_ip, output_file):
        self.interface = interface
        self.target_ip = target_ip
        self.logger = self._setup_logger(output_file)
        
    def _setup_logger(self, output_file):
        logging.basicConfig(
            filename=output_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def packet_callback(self, packet):
        if packet.haslayer(TCP):
            self._analyze_tcp(packet)
        elif packet.haslayer(UDP):
            self._analyze_udp(packet)
            
    def _analyze_tcp(self, packet):
        if packet[TCP].dport == 4433:  # VPN port
            self.logger.info(f"[VPN Traffic] {packet[IP].src} -> {packet[IP].dst}")
        elif packet.haslayer(Raw):
            payload = packet[Raw].load
            self.logger.info(f"[Plaintext] {packet[IP].src} -> {packet[IP].dst}: {payload}")
    
    def start_capture(self, duration=60):
        print(f"[*] Starting capture on {self.interface} for {duration} seconds")
        sniff(
            iface=self.interface,
            filter=f"host {self.target_ip}",
            prn=self.packet_callback,
            timeout=duration
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", required=True, help="Network interface")
    parser.add_argument("-t", "--target", required=True, help="Target IP")
    parser.add_argument("-o", "--output", default="capture.log", help="Output file")
    args = parser.parse_args()
    
    analyzer = NetworkAnalyzer(args.interface, args.target, args.output)
    analyzer.start_capture()

if __name__ == "__main__":
    main()