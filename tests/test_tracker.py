import http.server
import socketserver
import threading
import unittest

from tracker import build_tracker_url, request_peers


INFO_HASH = bytes([216, 247, 57, 206, 195, 40, 149, 108, 204, 91, 191, 31, 134, 217, 253, 207, 219, 168, 206, 182])
PEER_ID = bytes(range(1, 21))


class TrackerTests(unittest.TestCase):
    def test_build_tracker_url(self) -> None:
        url = build_tracker_url(
            "http://bttracker.debian.org:6969/announce",
            INFO_HASH,
            PEER_ID,
            6882,
            351272960,
        )
        self.assertIn("info_hash=%D8%F79%CE%C3%28%95l%CC%5B%BF%1F%86%D9%FD%CF%DB%A8%CE%B6", url)
        self.assertIn("peer_id=%01%02%03%04%05%06%07%08%09%0A%0B%0C%0D%0E%0F%10%11%12%13%14", url)
        self.assertTrue(url.startswith("http://bttracker.debian.org:6969/announce?"))

    def test_request_peers(self) -> None:
        payload = (
            b"d8:intervali900e5:peers12:"
            + bytes([192, 0, 2, 123, 0x1A, 0xE1, 127, 0, 0, 1, 0x1A, 0xE9])
            + b"e"
        )

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # type: ignore[override]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format, *args):  # pragma: no cover - silence logs
                return

        with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            host, port = server.server_address
            announce = f"http://{host}:{port}"
            peers = request_peers(announce, INFO_HASH, PEER_ID, 6882, 351272960)
            self.assertEqual(len(peers), 2)
            self.assertEqual(peers[0].ip, "192.0.2.123")
            self.assertEqual(peers[0].port, 6881)
            self.assertEqual(peers[1].ip, "127.0.0.1")
            self.assertEqual(peers[1].port, 6889)
            server.shutdown()


if __name__ == "__main__":
    unittest.main()


