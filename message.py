"""BitTorrent peer wire message helpers."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO, Optional

from wire import read_exact


class MessageID(IntEnum):
    CHOKE = 0
    UNCHOKE = 1
    INTERESTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8


@dataclass
class Message:
    msg_id: MessageID
    payload: bytes = b""

    def serialize(self) -> bytes:
        length = len(self.payload) + 1
        return struct.pack(">IB", length, self.msg_id) + self.payload

    def name(self) -> str:
        mapping = {
            MessageID.CHOKE: "Choke",
            MessageID.UNCHOKE: "Unchoke",
            MessageID.INTERESTED: "Interested",
            MessageID.NOT_INTERESTED: "NotInterested",
            MessageID.HAVE: "Have",
            MessageID.BITFIELD: "Bitfield",
            MessageID.REQUEST: "Request",
            MessageID.PIECE: "Piece",
            MessageID.CANCEL: "Cancel",
        }
        return mapping.get(self.msg_id, f"Unknown#{int(self.msg_id)}")

    def __str__(self) -> str:
        return f"{self.name()} [{len(self.payload)}]"


def serialize_keep_alive() -> bytes:
    return b"\x00\x00\x00\x00"


def read_message(stream: BinaryIO) -> Optional[Message]:
    length_raw = read_exact(stream, 4)
    (length,) = struct.unpack(">I", length_raw)
    if length == 0:
        return None
    payload = read_exact(stream, length)
    msg_id = MessageID(payload[0])
    return Message(msg_id=msg_id, payload=payload[1:])


def format_request(index: int, begin: int, length: int) -> Message:
    payload = struct.pack(">III", index, begin, length)
    return Message(msg_id=MessageID.REQUEST, payload=payload)


def format_have(index: int) -> Message:
    payload = struct.pack(">I", index)
    return Message(msg_id=MessageID.HAVE, payload=payload)


def parse_piece(index: int, buf: bytearray, msg: Message) -> int:
    if msg.msg_id != MessageID.PIECE:
        raise ValueError(f"Expected PIECE (ID {MessageID.PIECE}), got {msg.msg_id}")
    if len(msg.payload) < 8:
        raise ValueError("Payload too short")

    parsed_index, begin = struct.unpack(">II", msg.payload[:8])
    if parsed_index != index:
        raise ValueError(f"Expected index {index}, got {parsed_index}")
    if begin >= len(buf):
        raise ValueError("Begin offset too high")

    data = msg.payload[8:]
    end = begin + len(data)
    if end > len(buf):
        raise ValueError("Data exceeds buffer")
    buf[begin:end] = data
    return len(data)


def parse_have(msg: Message) -> int:
    if msg.msg_id != MessageID.HAVE:
        raise ValueError("Expected HAVE message")
    if len(msg.payload) != 4:
        raise ValueError("Expected payload length 4")
    (index,) = struct.unpack(">I", msg.payload)
    return index


