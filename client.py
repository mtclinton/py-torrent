"""Peer TCP client abstraction."""

from __future__ import annotations

import socket
from dataclasses import dataclass

from bitfield import BitField
from handshake import Handshake
from message import Message, MessageID, format_have, format_request, read_message
from peers import Peer


@dataclass
class Client:
    peer: Peer
    peer_id: bytes
    info_hash: bytes

    def __post_init__(self) -> None:
        self.conn = socket.create_connection(self.peer.address(), timeout=3)
        self.conn.settimeout(3)
        self._complete_handshake()
        self.bitfield = self._recv_bitfield()
        self.choked = True

    def _complete_handshake(self) -> None:
        hs = Handshake.create(self.info_hash, self.peer_id)
        self.conn.sendall(hs.serialize())
        res = Handshake.read(self.conn)
        if res.info_hash != self.info_hash:
            raise ValueError("Peer info hash mismatch")
        self.conn.settimeout(None)

    def _recv_bitfield(self) -> BitField:
        self.conn.settimeout(5)
        msg = read_message(self.conn)
        if msg is None:
            raise ValueError("Expected bitfield message, got keep-alive")
        if msg.msg_id != MessageID.BITFIELD:
            raise ValueError(f"Expected bitfield, got {msg.msg_id}")
        self.conn.settimeout(None)
        return BitField.from_bytes(msg.payload)

    def read(self) -> Message | None:
        return read_message(self.conn)

    def send_request(self, index: int, begin: int, length: int) -> None:
        self.conn.sendall(format_request(index, begin, length).serialize())

    def send_interested(self) -> None:
        self.conn.sendall(Message(MessageID.INTERESTED).serialize())

    def send_not_interested(self) -> None:
        self.conn.sendall(Message(MessageID.NOT_INTERESTED).serialize())

    def send_unchoke(self) -> None:
        self.conn.sendall(Message(MessageID.UNCHOKE).serialize())

    def send_have(self, index: int) -> None:
        self.conn.sendall(format_have(index).serialize())

    def close(self) -> None:
        try:
            self.conn.close()
        except OSError:
            pass

    def __enter__(self) -> "Client":  # pragma: no cover - convenience
        return self

    def __exit__(self, *exc) -> None:  # pragma: no cover - convenience
        self.close()


