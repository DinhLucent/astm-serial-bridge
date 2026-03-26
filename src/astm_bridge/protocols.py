import logging

# ASTM Control Characters
ENQ = b'\x05'
ACK = b'\x06'
NAK = b'\x15'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ETB = b'\x17'
LF = b'\x0a'
CR = b'\x0d'

class ASTMProtocolError(Exception):
    """Base class for ASTM protocol errors."""
    pass

class ASTMFrame:
    """Represents a single ASTM E1381 frame."""
    def __init__(self, sequence: int, data: str, is_last: bool = True):
        self.sequence = sequence % 8
        self.data = data
        self.is_last = is_last

    def encode(self) -> bytes:
        terminator = ETX if self.is_last else ETB
        # Frame format: <STX>seq data <terminator>CS1 CS2 <CR><LF>
        frame_content = str(self.sequence).encode() + self.data.encode() + terminator
        checksum = self.calculate_checksum(frame_content)
        return STX + frame_content + checksum + CR + LF

    @staticmethod
    def calculate_checksum(data: bytes) -> bytes:
        """Calculates 8-bit checksum as two hex characters."""
        checksum = sum(data) % 256
        return f"{checksum:02X}".upper().encode()

class ASTMLayer:
    """Handles ASTM logical layer (E1394)."""
    def __init__(self):
        self.logger = logging.getLogger("ASTMBridge")

    def parse_record(self, record_data: str) -> dict:
        """Parses an ASTM record into components."""
        if not record_data:
            return {}
        
        parts = record_data.split('|')
        record_type = parts[0]
        
        # Basic mapping of record types
        result = {"type": record_type}
        
        if record_type == 'H':
            result["name"] = "Header"
            result["sender_id"] = parts[4] if len(parts) > 4 else ""
        elif record_type == 'P':
            result["name"] = "Patient"
            result["patient_id"] = parts[3] if len(parts) > 3 else ""
            result["name_full"] = parts[5] if len(parts) > 5 else ""
        elif record_type == 'O':
            result["name"] = "Order"
            result["sample_id"] = parts[2] if len(parts) > 2 else ""
            result["test_id"] = parts[4] if len(parts) > 4 else ""
        elif record_type == 'R':
            result["name"] = "Result"
            result["test_id"] = parts[2] if len(parts) > 2 else ""
            result["value"] = parts[3] if len(parts) > 3 else ""
            result["units"] = parts[4] if len(parts) > 4 else ""
        elif record_type == 'L':
            result["name"] = "Terminator"
            
        return result
