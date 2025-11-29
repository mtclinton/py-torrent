"""Implementation of the BitTorrent handshake message."""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

from wire import read_exact

PSTR = "BitTorrent protocol"


@dataclass
class Handshake:
    pstr: str
    info_hash: bytes
    peer_id: bytes

    def serialize(self) -> bytes:
        pstr_bytes = self.pstr.encode("utf-8")
        buf = bytearray(len(pstr_bytes) + 49)
        buf[0] = len(pstr_bytes)
        cursor = 1
        buf[cursor : cursor + len(pstr_bytes)] = pstr_bytes
        cursor += len(pstr_bytes)
        cursor += 8  # Reserved bytes left at zero
        buf[cursor : cursor + 20] = self.info_hash
        cursor += 20
        buf[cursor : cursor + 20] = self.peer_id
        return bytes(buf)

    @classmethod
    def create(cls, info_hash: bytes, peer_id: bytes, pstr: str = PSTR) -> "Handshake":
        if len(info_hash) != 20 or len(peer_id) != 20:
            raise ValueError("info_hash and peer_id must be 20 bytes long")
        return cls(pstr=pstr, info_hash=info_hash, peer_id=peer_id)

    @classmethod
    def read(cls, stream: BinaryIO) -> "Handshake":
        try:
            length_raw = read_exact(stream, 1)
        except EOFError as exc:
            raise ValueError("Unexpected EOF while reading handshake length") from exc
        pstrlen = length_raw[0]
        if pstrlen == 0:
            raise ValueError("pstrlen cannot be 0")

        try:
            payload = read_exact(stream, 48 + pstrlen)
        except EOFError as exc:
            raise ValueError("Unexpected EOF while reading handshake payload") from exc
        pstr = payload[:pstrlen].decode("utf-8")
        info_hash = payload[pstrlen + 8 : pstrlen + 28]
        peer_id = payload[pstrlen + 28 : pstrlen + 48]
        if len(info_hash) != 20 or len(peer_id) != 20:
            raise ValueError("Invalid handshake payload length")
        return cls(pstr=pstr, info_hash=info_hash, peer_id=peer_id)

