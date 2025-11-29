"""Minimal bencode encoder/decoder needed by the BitTorrent client."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple


class BencodeError(ValueError):
    """Raised when bencoded data cannot be parsed."""


def _ensure_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise TypeError(f"Expected bytes or str, got {type(value)!r}")


def encode(value: Any) -> bytes:
    """Encode a Python object into bencode."""
    if isinstance(value, bool):
        # bool is a subclass of int, but we treat explicitly for clarity.
        value = int(value)

    if isinstance(value, int):
        return b"i" + str(value).encode("ascii") + b"e"

    if isinstance(value, (bytes, bytearray, memoryview, str)):
        data = _ensure_bytes(bytes(value))
        return str(len(data)).encode("ascii") + b":" + data

    if isinstance(value, (list, tuple)):
        return b"l" + b"".join(encode(item) for item in value) + b"e"

    if isinstance(value, dict):
        items: Iterable[Tuple[bytes, Any]] = (
            (_ensure_bytes(key), val) for key, val in value.items()
        )
        encoded_items = sorted(items, key=lambda kv: kv[0])
        buf = bytearray(b"d")
        for key, val in encoded_items:
            buf.extend(encode(key))
            buf.extend(encode(val))
        buf.extend(b"e")
        return bytes(buf)

    raise TypeError(f"Cannot bencode value of type {type(value)!r}")


def decode(data: bytes | bytearray | memoryview) -> Any:
    """Decode bencoded bytes into Python objects."""
    buf = memoryview(data).tobytes()

    value, next_index = _decode_value(buf, 0)
    if next_index != len(buf):
        raise BencodeError("Extra data after valid bencode payload")
    return value


def _decode_value(buf: bytes, index: int) -> Tuple[Any, int]:
    if index >= len(buf):
        raise BencodeError("Unexpected end of data")

    token = buf[index : index + 1]

    if token == b"i":
        end = buf.find(b"e", index)
        if end == -1:
            raise BencodeError("Integer value missing terminator")
        number = int(buf[index + 1 : end])
        return number, end + 1

    if token == b"l":
        index += 1
        items = []
        while True:
            if index >= len(buf):
                raise BencodeError("List value missing terminator")
            if buf[index : index + 1] == b"e":
                return items, index + 1
            item, index = _decode_value(buf, index)
            items.append(item)

    if token == b"d":
        index += 1
        mapping: Dict[bytes, Any] = {}
        previous_key = None
        while True:
            if index >= len(buf):
                raise BencodeError("Dictionary value missing terminator")
            if buf[index : index + 1] == b"e":
                return mapping, index + 1

            key, index = _decode_value(buf, index)
            if not isinstance(key, (bytes, bytearray)):
                raise BencodeError("Dictionary keys must be byte strings")
            key_bytes = bytes(key)
            if previous_key is not None and previous_key > key_bytes:
                # Dictionaries must be sorted; we allow unsorted but keep value.
                previous_key = key_bytes
            else:
                previous_key = key_bytes
            value, index = _decode_value(buf, index)
            mapping[key_bytes] = value

    if b"0" <= token <= b"9":
        colon = buf.find(b":", index)
        if colon == -1:
            raise BencodeError("String length missing delimiter")
        try:
            length = int(buf[index:colon])
        except ValueError as exc:
            raise BencodeError("Invalid string length") from exc
        start = colon + 1
        end = start + length
        if end > len(buf):
            raise BencodeError("Declared string length exceeds buffer")
        return buf[start:end], end

    raise BencodeError(f"Unknown token: {token!r}")


