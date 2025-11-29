"""Helpers for reading and writing from sockets/streams."""

from __future__ import annotations

from typing import BinaryIO, Protocol


class Reader(Protocol):
    def read(self, size: int) -> bytes:  # pragma: no cover - protocol definition
        ...


def read_exact(stream: BinaryIO | Reader, size: int) -> bytes:
    """Read exactly *size* bytes from a socket or file-like object."""
    remaining = size
    chunks = bytearray()
    while remaining:
        if hasattr(stream, "recv"):
            chunk = stream.recv(remaining)  # type: ignore[attr-defined]
        else:
            chunk = stream.read(remaining)
        if not chunk:
            raise EOFError("Unexpected EOF while reading from stream")
        chunks.extend(chunk)
        remaining -= len(chunk)
    return bytes(chunks)


