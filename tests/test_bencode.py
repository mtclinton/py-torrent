import unittest

import bencode


class BencodeTests(unittest.TestCase):
    def test_encode_decode_roundtrip(self) -> None:
        payload = {
            b"announce": b"http://tracker",
            b"info": {
                b"name": b"file.iso",
                b"length": 42,
                b"pieces": b"abcd" * 5,
                b"piece length": 16384,
            },
        }
        encoded = bencode.encode(payload)
        decoded = bencode.decode(encoded)
        self.assertEqual(decoded, payload)

    def test_decode_errors(self) -> None:
        with self.assertRaises(bencode.BencodeError):
            bencode.decode(b"i12")


if __name__ == "__main__":
    unittest.main()


