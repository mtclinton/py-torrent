import unittest

from bitfield import BitField


class BitFieldTests(unittest.TestCase):
    def test_has_piece(self) -> None:
        bf = BitField.from_bytes(bytes([0b01010100, 0b01010100]))
        outputs = [
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            False,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        for index, expected in enumerate(outputs):
            self.assertEqual(bf.has_piece(index), expected)

    def test_set_piece(self) -> None:
        inputs = [
            (4, [0b01011100, 0b01010100]),
            (9, [0b01010100, 0b01010100]),  # noop
            (15, [0b01010100, 0b01010101]),
            (19, [0b01010100, 0b01010100]),  # noop
        ]
        for index, expected in inputs:
            bf = BitField.from_bytes(bytes([0b01010100, 0b01010100]))
            bf.set_piece(index)
            self.assertEqual(list(bf.data), expected)


if __name__ == "__main__":
    unittest.main()


