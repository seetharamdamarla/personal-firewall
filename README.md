# Personal Firewall using Python

A **personal firewall** is an essential security component that monitors and controls incoming and outgoing network traffic based on predefined rules. This project implements a **Python-based custom firewall** designed for individual users and developers who want deeper visibility and control over the network packets traversing their system.

Unlike traditional firewalls, this tool gives **real-time packet analysis**, **rule-based filtering**, and a **user-friendly graphical interface** to add, remove, or manage firewall rules without diving deep into terminal commands or system configurations.

Whether you're learning cybersecurity, developing network-aware applications, or looking for a lightweight packet filtering solution—this project provides a great hands-on experience.

---

## 📁 Project Structure

personal-firewall/ <br>
├── firewall.py # Main packet sniffer and filtering logic <br>
├── logger.py # Logging system for packet activities <br>
├── utils.py # Helper functions for packet handling <br>
├── iptables.py # OS-level command integration (iptables) <br>
├── gui.py # GUI to view, add, and delete rules <br>
├── rules.json # JSON-based rule definitions <br>
├── logs.txt # Logs for blocked or allowed traffic <br>
├── .gitignore # Ignored files (.venv, pycache, etc.) <br>
└── requirements.txt # Required packages 


---

## 🔍 Module Descriptions

### `firewall.py`
The core of the firewall. It uses `Scapy` to sniff network packets in real time and checks them against rules from `rules.json`. Based on the match, it allows or blocks packets and logs the activity.

---

### `logger.py`
Handles all logging functionality. Every packet decision (ALLOW or BLOCK) is logged in `logs.txt` with timestamp and details.

---

### `utils.py`
Provides helper functions for:
- Extracting IPs and ports
- Mapping protocol numbers to names
- Packet formatting

Keeps code modular and clean.

---

### `iptables.py`
Provides optional integration with Linux's `iptables` to block or allow traffic at the system level.

---

### `gui.py`
A Tkinter-based GUI interface that lets you:
- Add or remove firewall rules
- View existing rules
- Control the firewall visually

---

### `rules.json`
Contains all firewall rules in JSON format. These rules define which packets to allow or block.

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

## Start the firewall
```bash
sudo python3 firewall.py
```

## 🛠 Tools & Technologies

Python 3

Scapy – For packet sniffing

Tkinter – GUI

JSON – Rule storage

iptables (Linux) – System-level packet filtering (optional)

## ✅ Features
Real-time packet sniffing

IP/Port/Protocol-based filtering

Rule management via GUI

Logging of all decisions

Optional iptables integration

## ⚠️ Notes
Designed for Linux

Requires sudo to sniff packets

GUI is optional but enhances usability

## 📜 License
This project is released under the MIT License.

## 🔚 Conclusion
This personal firewall project blends the power of packet sniffing, rule-based filtering, and user-friendly design into a compact security tool. Whether you're a beginner exploring cybersecurity or a developer seeking control over network traffic, this project offers a practical and educational solution. 
