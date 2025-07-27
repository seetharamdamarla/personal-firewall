from datetime import datetime
from utils import extract_packet_info

def log_packet(packet,action):
    with open("logs.txt","a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        src,dst,sport,dport,proto_str = extract_packet_info(packet)
        f.write(f"[{timestamp}] {action} | Src: {src}:{sport} -> Dst: {dst}:{dport} | Proto: {proto_str}\n")


