# astm-serial-bridge

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Protocol](https://img.shields.io/badge/Protocol-ASTM_LIS01--A2-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A professional bridge for connecting clinical laboratory instruments (using ASTM LIS01-A2/E1381) to modern TCP/IP backend systems. It handles RS-232 serial framing, checksum validation, and E1394 record parsing with a focus on data integrity for medical metrics.

## What is the ASTM Protocol?

The ASTM LIS01-A2 (formerly E1381) standard defines the low-level communication between medical devices and host systems. It uses a specific framing structure to ensure that clinical records (Patient info, Test results) are transmitted without corruption over serial lines.

## How it works

This bridge acts as a protocol translator:
1. **Serial Layer**: Listens for ASTM control characters (`ENQ`, `STX`, `EOT`).
2. **Framing Layer**: Assembled multiple frames into complete clinical records, validating the 8-bit checksum for every frame.
3. **Logical Layer**: Parses E1394 records (Header, Patient, Order, Result) into structured Python dictionaries for easy API consumption.

## Quick Start

### Process incoming frames

```python
from astm_bridge.protocols import FrameAssembler, ASTMLayer

assembler = FrameAssembler()
layer = ASTMLayer()

# Simulated incoming ASTM frame bytes
frame_bytes = b"\x021H|\\^&|||LAB123\x036A\r\x0a"

# Push frame to the stateful assembler
record_str = assembler.push_frame(frame_bytes)

if record_str:
    # Parse the logical record
    data = layer.parse_record(record_str)
    print(f"Received record type: {data['type']}")
    print(f"Sender: {data['sender_id']}")
```

## Features

- **Stateful Frame Assembly**: Automatically reconstructs clinical records that span multiple ASTM frames.
- **Checksum Validation**: Rigorous 8-bit hex checksum verification for every received frame.
- **E1394 Parsing**: Pre-built logic for common record types:
    - `H`: Message Header
    - `P`: Patient Information
    - `O`: Test Order
    - `R`: Results (Test Values, Units)
    - `L`: Message Terminator
- **Async Ready**: Designed for integration into `asyncio` serial loops.
- **Zero-Dependency**: No external libraries required for core protocol logic.

## Project Structure

```
astm-serial-bridge/
├── src/
│   └── astm_bridge/
│       ├── __init__.py
│       ├── bridge.py       # Async orchestrator (Skeleton)
│       └── protocols.py    # Framing, Checksums, and Record parsing
├── tests/
│   ├── test_protocols.py   # Protocol verification suite
│   └── test_placeholder.py
├── docs/                   # ASTM technical references
├── examples/               # Serial loop integration examples
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

```bash
git clone https://github.com/DinhLucent/astm-serial-bridge.git
cd astm-serial-bridge
pip install -r requirements.txt
```

## Running Tests

The test suite verifies checksum calculation, multi-frame reconstruction, and record parsing accuracy.

```bash
python -m pytest tests/test_protocols.py -v
```

## License

MIT License — see [LICENSE](LICENSE)

---
Built by [DinhLucent](https://github.com/DinhLucent)
