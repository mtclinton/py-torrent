"""Parsing .torrent files and coordinating downloads."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import List

import p2p
from bencode import decode, encode
from tracker import request_peers

PORT = 6881


@dataclass
class TorrentFile:
    announce: str
    info_hash: bytes
    piece_hashes: List[bytes]
    piece_length: int
    length: int
    name: str

    def download_to_file(self, path: str) -> None:
        peer_id = os.urandom(20)
        peers = request_peers(
            self.announce, self.info_hash, peer_id, PORT, self.length
        )
        torrent = p2p.Torrent(
            peers=peers,
            peer_id=peer_id,
            info_hash=self.info_hash,
            piece_hashes=self.piece_hashes,
            piece_length=self.piece_length,
            length=self.length,
            name=self.name,
        )
        data = torrent.download()
        with open(path, "wb") as handle:
            handle.write(data)


def _split_piece_hashes(pieces_blob: bytes) -> List[bytes]:
    hash_len = 20
    if len(pieces_blob) % hash_len != 0:
        raise ValueError("Received malformed pieces")
    return [
        pieces_blob[i : i + hash_len] for i in range(0, len(pieces_blob), hash_len)
    ]


def _to_torrent_file(payload: dict) -> TorrentFile:
    announce = payload[b"announce"].decode("utf-8")
    info = payload[b"info"]
    info_hash = hashlib.sha1(encode(info)).digest()
    pieces = _split_piece_hashes(info[b"pieces"])
    piece_length = int(info[b"piece length"])
    length = int(info[b"length"])
    name = info[b"name"].decode("utf-8")
    return TorrentFile(
        announce=announce,
        info_hash=info_hash,
        piece_hashes=pieces,
        piece_length=piece_length,
        length=length,
        name=name,
    )


def open_torrent(path: str) -> TorrentFile:
    with open(path, "rb") as handle:
        data = handle.read()
    payload = decode(data)
    if not isinstance(payload, dict):
        raise ValueError("Invalid torrent file")
    return _to_torrent_file(payload)

