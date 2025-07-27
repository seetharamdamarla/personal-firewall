import queue
import threading
from scapy.all import sniff, conf
from scapy.layers.inet import IP, TCP, UDP
from utils import ip_in_list, port_in_list, load_rules
from logger import log_packet
from gui import start_gui

packet_queue = queue.Queue()
threading.Thread(target=start_gui, args=(packet_queue,), daemon=True).start()

rules = load_rules()
conf.verb = 0  # Suppress Scapy logs

def packet_filter(pkt):
    if IP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        proto = pkt[IP].proto
        proto_str = {
            1: 'ICMP',
            2: 'IGMP',
            6: 'TCP',
            17: 'UDP'
        }.get(proto, str(proto))
        src_port = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else None)
        dst_port = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else None)
        action = 'ALLOWED'

        if ip_in_list(src_ip, rules['block_ips']) or ip_in_list(dst_ip, rules['block_ips']):
            action = 'BLOCKED'
        elif not ip_in_list(src_ip, rules['allow_ips']) and not ip_in_list(dst_ip, rules['allow_ips']):
            action = 'BLOCKED'
        elif proto_str in rules['block_protocols']:
            action = 'BLOCKED'
        elif port_in_list(src_port, rules['block_ports']) or port_in_list(dst_port, rules['block_ports']):
            action = 'BLOCKED'

        log_packet(pkt, action)
        packet_queue.put({'action': action, 'src_ip': src_ip, 'protocol': proto_str})

sniff(prn=packet_filter, store=False)
