import subprocess
import logging

logger = logging.getLogger(__name__)
TABLE = "personal_firewall"
CHAIN = "input"

def run_cmd(cmd: list) -> bool:
    try:
        # Requires sudo privileges without password
        subprocess.run(["sudo"] + cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"nftables error: {e.stderr}")
        return False

def ensure_table():
    run_cmd(["nft", "add", "table", "inet", TABLE])
    run_cmd(["nft", "add", "chain", "inet", TABLE, CHAIN, "{ type filter hook input priority filter - 1; policy accept; }"])

def block_ip(ip: str) -> bool:
    ensure_table()
    # Check if already blocked to avoid duplicates
    if ip in get_blocked_ips():
        return True
    return run_cmd(["nft", "add", "rule", "inet", TABLE, CHAIN, "ip", "saddr", ip, "drop"])

def unblock_ip(ip: str) -> bool:
    ensure_table()
    try:
        result = subprocess.run(["sudo", "nft", "-a", "list", "chain", "inet", TABLE, CHAIN], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        handle = None
        for line in lines:
            if f"saddr {ip} drop" in line:
                parts = line.strip().split()
                if "handle" in parts:
                    handle = parts[parts.index("handle") + 1]
                    break
        
        if handle:
            return run_cmd(["nft", "delete", "rule", "inet", TABLE, CHAIN, "handle", handle])
        return False
    except Exception as e:
        logger.error(f"Error unblocking: {e}")
        return False
        
def get_blocked_ips() -> list:
    try:
        result = subprocess.run(["sudo", "nft", "list", "chain", "inet", TABLE, CHAIN], capture_output=True, text=True)
        ips = []
        for line in result.stdout.split('\n'):
            if "drop" in line and "saddr" in line:
                parts = line.strip().split()
                if "saddr" in parts:
                    idx = parts.index("saddr")
                    if idx + 1 < len(parts):
                        ips.append(parts[idx+1])
        return ips
    except Exception:
        return []
