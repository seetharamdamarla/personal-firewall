# 🛡️ Personal Firewall — SOC Analyst Demo Environment

A full Security Operations Center (SOC) demo environment featuring dual-SIEM architecture (Splunk + Wazuh), automated threat detection, and live incident response — built for cybersecurity portfolio interviews.

## 🏗️ Architecture

```
Kali (attack) → Ubuntu NIC → Scapy sniffer + Suricata IDS
  → Suricata EVE JSON → Splunk (Network SIEM)
  → Wazuh agent → Wazuh Manager (Host-based IDS)
  → Splunk correlation → webhook → FastAPI → nftables DROP
  → Wazuh active response → nftables DROP
  → FastAPI → WebSocket → React SOC Dashboard (live updates)
  → SQLite (alert history)
```

## 🧰 Stack

| Layer | Component | Purpose |
|-------|-----------|---------|
| Network Capture | Scapy + Suricata | Packet sniffing + IDS rules |
| Host IDS | Wazuh (single-node) | FIM, auth monitoring, active response |
| Network SIEM | Splunk Free | Log aggregation, correlation, dashboards |
| Backend | FastAPI + SQLite | Alert API, nftables control, threat intel |
| Frontend | React + Recharts + Leaflet | Live SOC dashboard |
| Attacker | Kali Linux | Nmap, hping3, Hydra, Scapy |

## 📂 Project Structure

```
personal-firewall/
├── ubuntu-server/
│   ├── sniffer/          # Scapy packet capture daemon
│   ├── suricata/         # Custom Suricata rules (Phase 2)
│   ├── wazuh/            # Wazuh custom rules & configs (Phase 3)
│   ├── splunk/           # Splunk configs & dashboards (Phase 4)
│   └── netplan/          # Network configuration reference
├── backend/              # FastAPI application (Phase 5)
├── frontend/             # React SOC dashboard (Phase 6)
├── kali/                 # Attack simulator scripts (Phase 7)
├── .env.example          # Environment variable template
└── README.md
```

## 🚀 Build Phases

- [x] **Phase 1** — Lab Network Setup (UTM bridged networking, Scapy daemon)
- [ ] **Phase 2** — Suricata IDS + Custom Rules
- [ ] **Phase 3** — Wazuh Single-Node + Custom Rules
- [ ] **Phase 4** — Splunk + Universal Forwarder + Dashboards
- [ ] **Phase 5** — FastAPI Backend
- [ ] **Phase 6** — React SOC Dashboard
- [ ] **Phase 7** — Kali Attack Simulator
- [ ] **Phase 8** — End-to-End Testing + Documentation

## 🎯 Interview Demo Flow

1. Launch attack from Kali (Nmap scan or SYN flood)
2. Suricata detects network attack → logs to Splunk
3. Wazuh detects host events (failed SSH, file changes)
4. Auto-block fires via nftables within 5 seconds
5. React dashboard shows live alert feed + GeoIP map
6. Both Splunk and Wazuh dashboards visible side-by-side

## 📋 Prerequisites

- macOS with [UTM](https://mac.getutm.app/) installed
- Ubuntu Server 22.04 LTS VM (bridged networking)
- Kali Linux VM (bridged networking)
- Both VMs on the same bridged network segment

## ⚙️ Quick Start

1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your lab IPs
3. Follow the phase guides in order

---

*Built as a cybersecurity portfolio project demonstrating enterprise SOC architecture.*
