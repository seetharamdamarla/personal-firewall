#!/bin/bash
# ============================================================
# Personal Firewall — nftables Block Script (Wazuh Active Response)
# ============================================================
# Supports both Wazuh 4.x JSON stdin format AND manual CLI args.
# Called automatically by Wazuh execd when SSH brute force detected.
# Blocks attacker IP via nftables DROP rule.
# Logs blocks to /var/log/personal-firewall/blocks.jsonl
# ============================================================

LOG_FILE="/var/log/personal-firewall/blocks.jsonl"
BLOCK_TABLE="personal_firewall"
AR_LOG="/var/ossec/logs/active-responses.log"
mkdir -p /var/log/personal-firewall

# Wazuh 4.x sends JSON via stdin
read INPUT_JSON
ACTION=$(echo $INPUT_JSON | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null)
IP=$(echo $INPUT_JSON | python3 -c "import sys,json; d=json.load(sys.stdin); a=d.get('parameters',{}).get('alert',{}); print(a.get('data',{}).get('srcip', a.get('srcip','')))" 2>/dev/null)
RULEID=$(echo $INPUT_JSON | python3 -c "import sys,json; print(json.load(sys.stdin).get('parameters',{}).get('alert',{}).get('rule',{}).get('id','0'))" 2>/dev/null)

# Fallback: if called with command-line args (manual mode)
if [ -z "$ACTION" ] || [ -z "$IP" ]; then
    ACTION=$1; IP=$3; RULEID="${5:-0}"
fi

[ -z "$IP" ] && { echo "$(date): No IP provided" >> $AR_LOG; exit 1; }

# Ensure nftables table exists
nft list table inet $BLOCK_TABLE > /dev/null 2>&1 || {
    nft add table inet $BLOCK_TABLE
    nft add chain inet $BLOCK_TABLE input { type filter hook input priority -1 \; }
}

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

case "$ACTION" in
    add|Add)
        nft list chain inet $BLOCK_TABLE input 2>/dev/null | grep -q "saddr $IP drop" && exit 0
        nft add rule inet $BLOCK_TABLE input ip saddr $IP drop
        echo "{\"timestamp\":\"$TIMESTAMP\",\"action\":\"block\",\"src_ip\":\"$IP\",\"rule_id\":\"$RULEID\",\"source\":\"wazuh\"}" >> $LOG_FILE
        echo "$(date): BLOCKED $IP (rule $RULEID)" >> $AR_LOG
        ;;
    delete|Delete)
        HANDLE=$(nft -a list chain inet $BLOCK_TABLE input 2>/dev/null | grep "saddr $IP drop" | awk '{print $NF}')
        [ -n "$HANDLE" ] && nft delete rule inet $BLOCK_TABLE input handle $HANDLE
        echo "{\"timestamp\":\"$TIMESTAMP\",\"action\":\"unblock\",\"src_ip\":\"$IP\",\"source\":\"wazuh\"}" >> $LOG_FILE
        echo "$(date): UNBLOCKED $IP" >> $AR_LOG
        ;;
esac
exit 0
