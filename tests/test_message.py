import io
import unittest

import message
from message import Message, MessageID


class MessageTests(unittest.TestCase):
    def test_format_request(self) -> None:
        msg = message.format_request(4, 567, 4321)
        self.assertEqual(msg.msg_id, MessageID.REQUEST)
        self.assertEqual(msg.payload, b"\x00\x00\x00\x04\x00\x00\x02\x37\x00\x00\x10\xe1")

    def test_format_have(self) -> None:
        msg = message.format_have(4)
        self.assertEqual(msg.msg_id, MessageID.HAVE)
        self.assertEqual(msg.payload, b"\x00\x00\x00\x04")

    def test_parse_piece(self) -> None:
        buf = bytearray(10)
        msg = Message(
            msg_id=MessageID.PIECE,
            payload=b"\x00\x00\x00\x04\x00\x00\x00\x02\xaa\xbb\xcc\xdd\xee\xff",
        )
        n = message.parse_piece(4, buf, msg)
        self.assertEqual(n, 6)
        self.assertEqual(
            buf, bytearray(b"\x00\x00\xaa\xbb\xcc\xdd\xee\xff\x00\x00")
        )

    def test_parse_piece_invalid(self) -> None:
        buf = bytearray(10)
        msg = Message(msg_id=MessageID.CHOKE, payload=b"")
        with self.assertRaises(ValueError):
            message.parse_piece(4, buf, msg)

    def test_parse_have(self) -> None:
        msg = Message(msg_id=MessageID.HAVE, payload=b"\x00\x00\x00\x04")
        self.assertEqual(message.parse_have(msg), 4)

    def test_parse_have_invalid(self) -> None:
        msg = Message(msg_id=MessageID.HAVE, payload=b"\x00\x00\x04")
        with self.assertRaises(ValueError):
            message.parse_have(msg)

    def test_serialize(self) -> None:
        msg = Message(msg_id=MessageID.HAVE, payload=b"\x01\x02\x03\x04")
        self.assertEqual(msg.serialize(), b"\x00\x00\x00\x05\x04\x01\x02\x03\x04")

    def test_serialize_keep_alive(self) -> None:
        self.assertEqual(message.serialize_keep_alive(), b"\x00\x00\x00\x00")

    def test_read(self) -> None:
        stream = io.BytesIO(b"\x00\x00\x00\x05\x04\x01\x02\x03\x04")
        msg = message.read_message(stream)
        self.assertIsNotNone(msg)
        assert msg is not None
        self.assertEqual(msg.msg_id, MessageID.HAVE)
        self.assertEqual(msg.payload, b"\x01\x02\x03\x04")

    def test_read_keep_alive(self) -> None:
        stream = io.BytesIO(b"\x00\x00\x00\x00")
        self.assertIsNone(message.read_message(stream))

    def test_str(self) -> None:
        msg = Message(msg_id=MessageID.CHOKE, payload=b"\x01\x02")
        self.assertEqual(str(msg), "Choke [2]")


if __name__ == "__main__":
    unittest.main()


