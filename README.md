# 🏥 ASTM Serial/TCP Bridge

A production-quality Python bridge for medical device communication using the **ASTM E1381** (Low-level) and **ASTM E1394** (Logical layer) protocols.

## 🚀 Overview

This bridge facilitates data exchange between medical instruments (using RS-232 serial ports) and laboratory information systems (LIS) or other services via TCP/IP.

## ✨ Features

- **Protocol Support**: Implementation of ASTM E1381 framing and checksums.
- **Record Parsing**: Logic for parsing ASTM E1394 Header (H), Patient (P), Order (O), and Result (R) records.
- **Asynchronous**: Built on `asyncio` for high-concurrency and non-blocking I/O.
- **Flexible Adapter**: Bridge data from physical serial ports to reliable TCP streams.

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🛠️ Usage

```python
from astm_bridge import ASTMBridge, BridgeConfig

config = BridgeConfig(serial_port="COM3", tcp_port=5000)
bridge = ASTMBridge(config)

# Run the bridge
# await bridge.start()
```

## 📜 License

MIT
