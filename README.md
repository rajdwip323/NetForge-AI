# NetForge-AI

> **Smart Network Engineering Suite**

**AUTOMATE • ANALYZE • OPTIMIZE • SECURE**

NetForge-AI is a Python-based network engineering toolkit designed to help network engineers and learners **design, configure, analyze, automate, monitor, and troubleshoot networks** through practical engineering utilities.

The project is being developed as a practical networking platform with a strong focus on **IP addressing, subnetting, VLSM, network analysis, automation, monitoring, and AI-powered network assistance**.

---

## 🚀 Project Vision

NetForge-AI aims to become an all-in-one network engineering companion that combines:

* Network Design
* Configuration Assistance
* Network Automation
* IP & Subnet Analysis
* Network Monitoring
* Troubleshooting
* AI-Powered Network Insights
* Engineering Utilities

The long-term goal is to create a practical tool that can be useful for **network engineers, NOC engineers, telecom engineers, students, and networking learners**.

---

## 🎯 Core Capabilities

NetForge-AI is being developed around six major engineering actions:

| Capability       | Purpose                                                |
| ---------------- | ------------------------------------------------------ |
| **Design**       | Plan IP addressing and network structures              |
| **Configure**    | Generate and assist with network configurations        |
| **Automate**     | Automate repetitive network engineering tasks          |
| **Analyze**      | Analyze IP addresses, subnets, and network information |
| **Monitor**      | Monitor network devices and network health             |
| **Troubleshoot** | Detect problems and provide troubleshooting assistance |

---

## 🛠️ Current CLI Tools

The current CLI provides six working network engineering utilities:

### 1. IP Address Validator

Validates IPv4 and IP address input and identifies whether the supplied address is valid.

### 2. IPv4 / IPv6 Detector

Automatically identifies whether an address is:

* IPv4
* IPv6

### 3. Network Information

Provides network information from an IP address and subnet mask, including network-related addressing details.

### 4. Subnet Calculator

Calculates important subnet information from CIDR notation:

* Network Address
* Broadcast Address
* Prefix Length
* Subnet Mask
* Wildcard Mask
* Total Addresses
* Usable Hosts
* First Usable Host
* Last Usable Host

### 5. VLSM Calculator

Calculates Variable Length Subnet Masking (VLSM) based on host requirements.

Example:

```text
Network: 192.168.1.0/24

Requirements:
100 hosts
50 hosts
20 hosts
10 hosts
```

The calculator generates appropriate subnet sizes such as:

```text
100 hosts → /25
50 hosts  → /26
20 hosts  → /27
10 hosts  → /28
```

### 6. IP & Subnet Analyzer

Combines IP and subnet calculations into a single analysis utility for IPv4 CIDR input.

---

## 💻 CLI Menu

Current CLI menu:

```text
=======================================================
              NETFORGE-AI
       Smart Network Engineering Suite
=======================================================

1. IP Address Validator
2. IPv4 / IPv6 Detector
3. Network Information
4. Subnet Calculator
5. VLSM Calculator
6. IP & Subnet Analyzer
0. Exit
```

---

## ▶️ Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/rajdwip323/NetForge-AI.git
```

### 2. Enter the project directory

```bash
cd NetForge-AI
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Run the CLI

```powershell
python src/cli/main.py
```

---

## 🧪 Testing & Quality Assurance

NetForge-AI follows a test-driven development and QA-oriented workflow.

The current CLI has completed:

* Functional Testing
* Error Handling Testing
* CLI UX Testing
* Full Regression Testing

### Current QA Status

**🟢 FULL REGRESSION QA — PASS**

All six CLI tools have been tested with valid inputs.

Invalid/error scenarios have also been tested for the relevant tools.

A control-flow issue discovered during regression testing was identified, fixed, and successfully retested.

---

## 📁 Project Structure

```text
NetForge-AI/
│
├── src/
│   ├── ai/
│   ├── alerts/
│   ├── cli/
│   │   └── main.py
│   ├── config/
│   ├── core/
│   │   └── network_utils.py
│   ├── dashboard/
│   ├── database/
│   ├── discovery/
│   ├── monitoring/
│   ├── reports/
│   └── scripts/
│
├── tests/
├── docs/
├── logs/
├── diagrams/
│
├── README.md
└── .gitignore
```

---

## 🗺️ Roadmap

### Phase 1 — Foundation

**Status: ✅ Complete**

Completed foundation capabilities include:

* IP Validation
* IPv4 / IPv6 Detection
* Network Information
* CIDR Information
* Host Range
* Prefix Length
* Subnet Information
* Wildcard Mask

---

### Phase 2 — IP & Subnet Tools

**Status: 🚧 In Progress**

Completed:

* ✅ Subnet Calculator
* ✅ VLSM Calculator
* ✅ IP & Subnet Analyzer

Planned:

* ⏳ Supernet Calculator
* ⏳ IP Range Generator

---

### Phase 3 — Network Discovery & Testing

Planned capabilities:

* Device Discovery
* Ping Testing
* Network Scanning
* Connectivity Testing
* Interface Discovery

---

### Phase 4 — Network Monitoring

Planned capabilities:

* SNMP Monitoring
* SSH-based Monitoring
* CPU Monitoring
* Memory Monitoring
* Interface Monitoring
* Bandwidth Monitoring
* Device Health Monitoring

---

### Phase 5 — Database & Reporting

Planned capabilities:

* SQLite / PostgreSQL
* Historical Monitoring Data
* Network Reports
* Alert History
* Performance Reports

---

### Phase 6 — AI-Powered Network Engineering

Long-term AI capabilities:

* Intelligent Troubleshooting
* Log Analysis
* Network Anomaly Detection
* Automated Recommendations
* Configuration Assistance
* AI-powered Network Automation

---

### Phase 7 — GUI / Dashboard

Future dashboard vision:

* IP Intelligence
* Subnet Calculator
* VLSM Planner
* Network Analyzer
* Address Validator
* Network Test Center
* Monitoring Dashboard
* Alerts & Reports

---

## 🔮 Future Vision

The long-term objective is to evolve NetForge-AI from a CLI-based networking toolkit into a complete **Network Engineering Suite** with:

```text
                NETFORGE-AI
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    DESIGN       ANALYZE       CONFIGURE
       │             │             │
       └─────────────┼─────────────┘
                     │
                 AUTOMATE
                     │
              ┌──────┴──────┐
              │             │
           MONITOR      TROUBLESHOOT
              │             │
              └──────┬──────┘
                     │
                AI ENGINE
```

The project will progressively move from basic networking utilities toward **automation, monitoring, intelligent troubleshooting, and AI-assisted network engineering**.

---

## 📌 Current Development Status

```text
CLI Foundation              ✅ Complete
Core Networking Utilities   ✅ Complete
VLSM Calculator             ✅ Complete
Subnet Calculator           ✅ Complete
IP & Subnet Analyzer        ✅ Complete
CLI Integration             ✅ Complete
CLI Error Handling          ✅ Complete
Full Regression QA          ✅ PASS
Documentation               🔄 Current Phase
```

---

## 👨‍💻 Project

**NetForge-AI — Smart Network Engineering Suite**

GitHub:

https://github.com/rajdwip323/NetForge-AI

---

## 📜 License

This project is currently under active development.
