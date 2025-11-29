import io
import unittest

from handshake import Handshake, PSTR


INFO_HASH = bytes(
    [134, 212, 200, 0, 36, 164, 105, 190, 76, 80, 188, 90, 16, 44, 247, 23, 128, 49, 0, 116]
)
PEER_ID = bytes(range(1, 21))


class HandshakeTests(unittest.TestCase):
    def test_create(self) -> None:
        hs = Handshake.create(INFO_HASH, PEER_ID)
        self.assertEqual(hs.pstr, PSTR)
        self.assertEqual(hs.info_hash, INFO_HASH)
        self.assertEqual(hs.peer_id, PEER_ID)

    def test_serialize(self) -> None:
        hs = Handshake.create(INFO_HASH, PEER_ID)
        buf = hs.serialize()
        self.assertEqual(
            buf,
            bytes(
                [
                    19,
                    *b"BitTorrent protocol",
                    *([0] * 8),
                    *INFO_HASH,
                    *PEER_ID,
                ]
            ),
        )

    def test_read(self) -> None:
        payload = bytes(
            [19, *b"BitTorrent protocol", *([0] * 8), *INFO_HASH, *PEER_ID]
        )
        hs = Handshake.read(io.BytesIO(payload))
        self.assertEqual(hs.info_hash, INFO_HASH)
        self.assertEqual(hs.peer_id, PEER_ID)
        self.assertEqual(hs.pstr, "BitTorrent protocol")

    def test_read_invalid(self) -> None:
        with self.assertRaises(ValueError):
            Handshake.read(io.BytesIO(b""))


if __name__ == "__main__":
    unittest.main()


