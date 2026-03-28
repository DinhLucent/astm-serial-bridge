import logging
from typing import Optional

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

    def __repr__(self) -> str:
        return f"ASTMFrame(seq={self.sequence}, data_len={len(self.data)}, last={self.is_last})"

    @staticmethod
    def calculate_checksum(data: bytes) -> bytes:
        """Calculates 8-bit checksum as two hex characters."""
        checksum = sum(data) % 256
        return f"{checksum:02X}".upper().encode()


class FrameAssembler:
    """Stateful assembler for reconstruction of multi-frame ASTM messages."""
    def __init__(self):
        self.buffer = ""
        self.expected_seq = 1

    def push_frame(self, frame_bytes: bytes) -> Optional[str]:
        """Validate and add a frame to the buffer.
        Returns the full record string if this was the last frame, else None.
        """
        if not frame_bytes.startswith(STX):
            return None
        
        # Check integrity
        # Format: <STX>seq data <term>CS1 CS2 <CR><LF>
        # Minimum: STX(1) + SEQ(1) + TERM(1) + CS(2) + CR(1) + LF(1) = 7
        if len(frame_bytes) < 7:
            return None
            
        data_block = frame_bytes[1:-4]  # Remove STX and CS+CR+LF
        frame_cs = frame_bytes[-4:-2]
        
        calculated_cs = ASTMFrame.calculate_checksum(data_block)
        if frame_cs != calculated_cs:
            raise ASTMProtocolError(f"Checksum mismatch: got {frame_cs}, expected {calculated_cs}")
        
        seq = int(data_block[0:1].decode())
        content = data_block[1:-1].decode()
        terminator = data_block[-1:]
        
        self.buffer += content
        self.expected_seq = (seq + 1) % 8
        
        if terminator == ETX:
            complete = self.buffer
            self.buffer = ""
            self.expected_seq = 1
            return complete
        return None

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
