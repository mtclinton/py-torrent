"""Peer parsing helpers."""

from __future__ import annotations

import ipaddress
import struct
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Peer:
    ip: str
    port: int

    def address(self) -> tuple[str, int]:
        return self.ip, self.port

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.ip}:{self.port}"


def parse_compact_peers(peers_bin: bytes) -> List[Peer]:
    peer_size = 6
    if len(peers_bin) % peer_size != 0:
        raise ValueError("Received malformed peers")
    peers: List[Peer] = []
    for offset in range(0, len(peers_bin), peer_size):
        ip_raw = peers_bin[offset : offset + 4]
        port_raw = peers_bin[offset + 4 : offset + peer_size]
        ip_addr = str(ipaddress.IPv4Address(ip_raw))
        (port,) = struct.unpack(">H", port_raw)
        peers.append(Peer(ip=ip_addr, port=port))
    return peers


