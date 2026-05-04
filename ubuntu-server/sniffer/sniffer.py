#!/usr/bin/env python3
"""
Personal Firewall — Scapy Packet Capture Daemon
================================================
Sniffs all packets on the specified NIC, parses src/dst IP, port, protocol.
Writes structured JSON logs to /var/log/personal-firewall/packets.jsonl

Usage:
    sudo python3 sniffer.py

Environment Variables:
    SNIFFER_IFACE  — Network interface to sniff (default: enp0s1)
"""

import json
import os
import sys
import signal
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, conf

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
INTERFACE = os.environ.get("SNIFFER_IFACE", "enp0s1")
LOG_DIR = Path("/var/log/personal-firewall")
PACKET_LOG = LOG_DIR / "packets.jsonl"
STATS_INTERVAL = 60  # Print stats every N seconds

# Protocol number → name mapping
PROTO_MAP = {1: "ICMP", 6: "TCP", 17: "UDP"}

# ──────────────────────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "sniffer.log"),
    ],
)
logger = logging.getLogger("sniffer")

# ──────────────────────────────────────────────────────────────
# Stats tracking
# ──────────────────────────────────────────────────────────────
stats = {
    "total_packets": 0,
    "tcp": 0,
    "udp": 0,
    "icmp": 0,
    "arp": 0,
    "other": 0,
    "start_time": time.time(),
}


def log_stats():
    """Print capture statistics to the logger."""
    elapsed = time.time() - stats["start_time"]
    pps = stats["total_packets"] / elapsed if elapsed > 0 else 0
    logger.info(
        f"STATS | Total: {stats['total_packets']} | "
        f"TCP: {stats['tcp']} | UDP: {stats['udp']} | "
        f"ICMP: {stats['icmp']} | ARP: {stats['arp']} | "
        f"Other: {stats['other']} | "
        f"Rate: {pps:.1f} pkt/s | Uptime: {elapsed:.0f}s"
    )


def process_packet(pkt):
    """
    Parse a captured packet and write structured JSON to the log file.

    Extracts: timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
              tcp_flags, packet_size, icmp_type, icmp_code.
    """
    stats["total_packets"] += 1

    # Periodic stats logging
    if stats["total_packets"] % 1000 == 0:
        log_stats()

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": None,
        "dst_ip": None,
        "protocol": "OTHER",
        "src_port": None,
        "dst_port": None,
        "tcp_flags": None,
        "size": len(pkt),
        "iface": INTERFACE,
    }

    # ── ARP ──
    if pkt.haslayer(ARP):
        stats["arp"] += 1
        arp = pkt[ARP]
        record.update(
            {
                "protocol": "ARP",
                "src_ip": arp.psrc,
                "dst_ip": arp.pdst,
            }
        )
        write_record(record)
        return

    # ── IP layer required for everything else ──
    if not pkt.haslayer(IP):
        stats["other"] += 1
        return

    ip = pkt[IP]
    record["src_ip"] = ip.src
    record["dst_ip"] = ip.dst
    record["protocol"] = PROTO_MAP.get(ip.proto, f"PROTO_{ip.proto}")

    # ── TCP ──
    if pkt.haslayer(TCP):
        stats["tcp"] += 1
        tcp = pkt[TCP]
        record["src_port"] = tcp.sport
        record["dst_port"] = tcp.dport
        record["tcp_flags"] = str(tcp.flags)

    # ── UDP ──
    elif pkt.haslayer(UDP):
        stats["udp"] += 1
        udp = pkt[UDP]
        record["src_port"] = udp.sport
        record["dst_port"] = udp.dport

    # ── ICMP ──
    elif pkt.haslayer(ICMP):
        stats["icmp"] += 1
        icmp_pkt = pkt[ICMP]
        record["icmp_type"] = icmp_pkt.type
        record["icmp_code"] = icmp_pkt.code

    # ── Other IP protocols ──
    else:
        stats["other"] += 1

    write_record(record)


def write_record(record):
    """Append a JSON record to the packet log file."""
    try:
        with open(PACKET_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
    except IOError as e:
        logger.error(f"Failed to write packet record: {e}")


def shutdown(signum, frame):
    """Graceful shutdown handler."""
    logger.info(f"Received signal {signum} — shutting down...")
    log_stats()
    sys.exit(0)


def main():
    """Entry point — start the packet capture daemon."""
    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # Disable Scapy's verbose output
    conf.verb = 0

    logger.info("=" * 60)
    logger.info("Personal Firewall — Scapy Sniffer Daemon")
    logger.info(f"Interface: {INTERFACE}")
    logger.info(f"Packet log: {PACKET_LOG}")
    logger.info("=" * 60)

    # Verify interface exists
    try:
        from scapy.all import get_if_list
        available = get_if_list()
        if INTERFACE not in available:
            logger.error(
                f"Interface '{INTERFACE}' not found. Available: {available}"
            )
            sys.exit(1)
        logger.info(f"Interface '{INTERFACE}' confirmed available")
    except Exception as e:
        logger.warning(f"Could not enumerate interfaces: {e}")

    logger.info("Starting packet capture... (Ctrl+C to stop)")

    try:
        sniff(
            iface=INTERFACE,
            prn=process_packet,
            store=False,  # Don't store packets in memory — prevents RAM exhaustion
            filter="ip or arp",  # BPF filter: skip IPv6/L2 noise, capture only IPv4 + ARP
        )
    except PermissionError:
        logger.error(
            "Permission denied. Run with sudo or as root. "
            "Raw sockets require CAP_NET_RAW capability."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Sniff error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
