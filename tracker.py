"""HTTP tracker requests."""

from __future__ import annotations

import urllib.parse
import urllib.request
from typing import List

from bencode import decode
from peers import Peer, parse_compact_peers


def build_tracker_url(
    announce: str, info_hash: bytes, peer_id: bytes, port: int, left: int
) -> str:
    parsed = urllib.parse.urlparse(announce)
    base = parsed._replace(query="")
    params = [
        ("info_hash", urllib.parse.quote_from_bytes(info_hash)),
        ("peer_id", urllib.parse.quote_from_bytes(peer_id)),
        ("port", str(port)),
        ("uploaded", "0"),
        ("downloaded", "0"),
        ("compact", "1"),
        ("left", str(left)),
    ]
    query = "&".join(f"{key}={value}" for key, value in params)
    return urllib.parse.urlunparse(base._replace(query=query))


def request_peers(
    announce: str, info_hash: bytes, peer_id: bytes, port: int, left: int
) -> List[Peer]:
    url = build_tracker_url(announce, info_hash, peer_id, port, left)
    with urllib.request.urlopen(url, timeout=15) as response:
        data = response.read()
    payload = decode(data)
    peers_value = payload.get(b"peers")
    if not isinstance(peers_value, (bytes, bytearray)):
        raise ValueError("Tracker response missing compact peers")
    return parse_compact_peers(bytes(peers_value))


