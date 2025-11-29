"""Peer-to-peer coordination and piece downloading."""

from __future__ import annotations

import hashlib
import logging
import queue
import threading
from dataclasses import dataclass
from typing import List

from client import Client
from message import MessageID, parse_have, parse_piece
from peers import Peer

MAX_BLOCK_SIZE = 16384
MAX_BACKLOG = 5


@dataclass
class PieceWork:
    index: int
    hash_bytes: bytes
    length: int


@dataclass
class PieceResult:
    index: int
    data: bytes


@dataclass
class PieceProgress:
    index: int
    client: Client
    length: int
    buf: bytearray
    downloaded: int = 0
    requested: int = 0
    backlog: int = 0

    def read_message(self) -> None:
        msg = self.client.read()
        if msg is None:
            return
        if msg.msg_id == MessageID.UNCHOKE:
            self.client.choked = False
        elif msg.msg_id == MessageID.CHOKE:
            self.client.choked = True
        elif msg.msg_id == MessageID.HAVE:
            index = parse_have(msg)
            self.client.bitfield.set_piece(index)
        elif msg.msg_id == MessageID.PIECE:
            n = parse_piece(self.index, self.buf, msg)
            self.downloaded += n
            self.backlog -= 1


def attempt_download_piece(client: Client, piece: PieceWork) -> bytes:
    progress = PieceProgress(
        index=piece.index,
        client=client,
        length=piece.length,
        buf=bytearray(piece.length),
    )
    client.conn.settimeout(30)
    try:
        while progress.downloaded < piece.length:
            if not client.choked:
                while (
                    progress.backlog < MAX_BACKLOG and progress.requested < piece.length
                ):
                    block_size = min(
                        MAX_BLOCK_SIZE, piece.length - progress.requested
                    )
                    client.send_request(
                        piece.index, progress.requested, block_size
                    )
                    progress.backlog += 1
                    progress.requested += block_size
            progress.read_message()
        return bytes(progress.buf)
    finally:
        client.conn.settimeout(None)


def check_integrity(piece: PieceWork, data: bytes) -> None:
    digest = hashlib.sha1(data).digest()
    if digest != piece.hash_bytes:
        raise ValueError(f"Piece #{piece.index} failed integrity check")


@dataclass
class Torrent:
    peers: List[Peer]
    peer_id: bytes
    info_hash: bytes
    piece_hashes: List[bytes]
    piece_length: int
    length: int
    name: str

    def _piece_bounds(self, index: int) -> tuple[int, int]:
        begin = index * self.piece_length
        end = min(begin + self.piece_length, self.length)
        return begin, end

    def _piece_size(self, index: int) -> int:
        begin, end = self._piece_bounds(index)
        return end - begin

    def _start_worker(
        self,
        peer: Peer,
        work_queue: "queue.Queue[PieceWork | None]",
        results: "queue.Queue[PieceResult]",
    ) -> None:
        try:
            client = Client(peer=peer, peer_id=self.peer_id, info_hash=self.info_hash)
        except Exception as exc:  # pragma: no cover - network errors
            logging.warning("Handshake with %s failed: %s", peer, exc)
            return

        with client:
            logging.info("Connected to %s", peer)
            client.send_unchoke()
            client.send_interested()

            while True:
                try:
                    work = work_queue.get(timeout=5)
                except queue.Empty:
                    return
                if work is None:
                    work_queue.put(None)
                    return
                if not client.bitfield.has_piece(work.index):
                    work_queue.put(work)
                    continue
                try:
                    data = attempt_download_piece(client, work)
                    check_integrity(work, data)
                except Exception as exc:
                    logging.warning(
                        "Piece #%d failed from %s: %s", work.index, peer, exc
                    )
                    work_queue.put(work)
                    return

                client.send_have(work.index)
                results.put(PieceResult(index=work.index, data=data))

    def download(self) -> bytes:
        if not self.peers:
            raise ValueError("No peers available to download from")
        work_queue: "queue.Queue[PieceWork | None]" = queue.Queue()
        results: "queue.Queue[PieceResult]" = queue.Queue()
        for index, hash_bytes in enumerate(self.piece_hashes):
            length = self._piece_size(index)
            work_queue.put(PieceWork(index=index, hash_bytes=hash_bytes, length=length))

        threads = []
        for peer in self.peers:
            thread = threading.Thread(
                target=self._start_worker, args=(peer, work_queue, results), daemon=True
            )
            thread.start()
            threads.append(thread)

        buf = bytearray(self.length)
        completed = 0
        total_pieces = len(self.piece_hashes)
        while completed < total_pieces:
            result = results.get()
            begin, end = self._piece_bounds(result.index)
            buf[begin:end] = result.data
            completed += 1
            percent = (completed / total_pieces) * 100
            logging.info(
                "(%0.2f%%) Downloaded piece #%d", percent, result.index
            )

        for _ in threads:
            work_queue.put(None)
        for thread in threads:
            thread.join(timeout=1)

        return bytes(buf)


