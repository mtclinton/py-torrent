"""Bitfield helpers for peer piece availability tracking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BitField:
    """Represents the pieces a peer has announced."""

    data: bytearray

    @classmethod
    def from_bytes(cls, payload: bytes) -> "BitField":
        return cls(bytearray(payload))

    def has_piece(self, index: int) -> bool:
        byte_index = index // 8
        offset = index % 8
        if byte_index < 0 or byte_index >= len(self.data):
            return False
        return (self.data[byte_index] >> (7 - offset)) & 1 == 1

    def set_piece(self, index: int) -> None:
        byte_index = index // 8
        offset = index % 8
        if byte_index < 0 or byte_index >= len(self.data):
            return
        self.data[byte_index] |= 1 << (7 - offset)

    def raw(self) -> bytes:
        return bytes(self.data)


