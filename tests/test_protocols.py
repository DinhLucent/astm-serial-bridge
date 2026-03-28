"""Tests for ASTM protocol logic."""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astm_bridge.protocols import ASTMFrame, FrameAssembler, ASTMLayer, STX, ETX, ETB, CR, LF, ASTMProtocolError

def test_checksum_calculation():
    # Example from a known ASTM implementation
    data = b"1H|\\^&|||RECV|||||||P|1"
    cs = ASTMFrame.calculate_checksum(data)
    assert len(cs) == 2
    assert cs.isalnum()

def test_frame_encoding():
    frame = ASTMFrame(sequence=1, data=r"H|\^&|||RECV", is_last=True)
    encoded = frame.encode()
    assert encoded.startswith(STX)
    assert encoded.endswith(CR + LF)
    assert str(frame.sequence).encode() in encoded
    assert b"RECV" in encoded
    assert ETX in encoded

def test_assembler_single_frame():
    assembler = FrameAssembler()
    frame_data = r"H|\^&|||RECV"
    frame = ASTMFrame(sequence=1, data=frame_data, is_last=True)
    
    result = assembler.push_frame(frame.encode())
    assert result == frame_data

def test_assembler_multi_frame():
    assembler = FrameAssembler()
    
    # Frame 1 (Intermediate)
    f1_data = "P|1||12345||DOE^JOHN|"
    f1 = ASTMFrame(sequence=2, data=f1_data, is_last=False)
    r1 = assembler.push_frame(f1.encode())
    assert r1 is None
    
    # Frame 2 (Last)
    f2_data = "USA"
    f2 = ASTMFrame(sequence=3, data=f2_data, is_last=True)
    r2 = assembler.push_frame(f2.encode())
    
    assert r2 == f1_data + f2_data

def test_assembler_checksum_error():
    assembler = FrameAssembler()
    frame = ASTMFrame(sequence=1, data="DATA", is_last=True)
    raw = frame.encode()
    
    # Corrupt checksum (last 3 bytes are CS+CR+LF, so CS is at -4:-2)
    corrupted = raw[:-4] + b"ZZ" + raw[-2:]
    
    with pytest.raises(ASTMProtocolError):
        assembler.push_frame(corrupted)

def test_parser_records():
    layer = ASTMLayer()
    
    # Header
    h = layer.parse_record(r"H|\^&|||LAB123")
    assert h["type"] == "H"
    assert h["sender_id"] == "LAB123"
    
    # Patient
    p = layer.parse_record("P|1||PAT001||DOE^ALICE")
    assert p["type"] == "P"
    assert p["patient_id"] == "PAT001"
    assert p["name_full"] == "DOE^ALICE"
