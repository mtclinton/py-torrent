import unittest

from peers import Peer, parse_compact_peers


class PeerTests(unittest.TestCase):
    def test_parse_compact(self) -> None:
        payload = bytes(
            [127, 0, 0, 1, 0x00, 0x50, 1, 1, 1, 1, 0x01, 0xBB]
        )
        peers = parse_compact_peers(payload)
        self.assertEqual(
            peers,
            [
                Peer(ip="127.0.0.1", port=80),
                Peer(ip="1.1.1.1", port=443),
            ],
        )

    def test_parse_invalid_length(self) -> None:
        with self.assertRaises(ValueError):
            parse_compact_peers(bytes([127, 0, 0, 1, 0x00]))


if __name__ == "__main__":
    unittest.main()


