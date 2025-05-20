#!/usr/bin/env python3
from scapy.all import *
import logging

def packet_callback(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        payload = packet[Raw].load
        logging.info(f"Captured: {src_ip} -> {dst_ip}: {payload}")

def start_capture(interface):
    logging.basicConfig(
        filename='capture.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    
    print(f"[*] Starting capture on {interface}")
    print("[*] Writing output to capture.log")
    
    sniff(
        iface=interface,
        filter="host 192.168.100.20 and host 192.168.100.10",
        prn=packet_callback
    )

if __name__ == "__main__":
    start_capture("eth1")
