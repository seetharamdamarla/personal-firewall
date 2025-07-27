import json
import ipaddress
from scapy.layers.inet import TCP,UDP,IP

def ip_in_list(ip,ip_list):
    ip_obj = ipaddress.ip_address(ip)
    for net in ip_list:
        try:
            if ip_obj in ipaddress.ip_network(net,strict=False):
                return True
        except ValueError:
            continue
    return False

def port_in_list(port,port_list):
    if port is None:
        return False
    return int(port) in port_list

def load_rules():
    with open("rules.json") as f:
        return json.load(f)

def extract_packet_info(packet):
    src = packet[IP].src
    dst = packet[IP].dst
    proto = packet[IP].proto
    proto_str = {6:'TCP',17:'UDP'}.get(proto,str(proto))
    sport = packet[TCP].sport if TCP in packet else (packet[UDP].sport if UDP in packet else '-')
    dport = packet[TCP].dport if TCP in packet else (packet[UDP].dport if UDP in packet else '-')
    return  src,dst,sport,dport,proto_str
