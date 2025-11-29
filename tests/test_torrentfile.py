import hashlib
from pathlib import Path
import tempfile
import unittest

import bencode
from torrentfile import TorrentFile, open_torrent


class TorrentFileTests(unittest.TestCase):
    def test_open_torrent(self) -> None:
        info = {
            b"name": b"sample.bin",
            b"length": 8,
            b"piece length": 4,
            b"pieces": b"01234567890123456789",
        }
        data = {
            b"announce": b"http://tracker",
            b"info": info,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.torrent"
            path.write_bytes(bencode.encode(data))
            torrent = open_torrent(str(path))

        expected_hash = hashlib.sha1(bencode.encode(info)).digest()
        self.assertEqual(torrent.announce, "http://tracker")
        self.assertEqual(torrent.info_hash, expected_hash)
        self.assertEqual(torrent.piece_length, 4)
        self.assertEqual(torrent.length, 8)
        self.assertEqual(torrent.name, "sample.bin")
        self.assertEqual(torrent.piece_hashes, [b"01234567890123456789"])


if __name__ == "__main__":
    unittest.main()


