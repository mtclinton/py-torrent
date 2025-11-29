from __future__ import annotations

import argparse
import sys

from console import configure_logging
from torrentfile import open_torrent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download a file via BitTorrent")
    parser.add_argument("torrent", help=".torrent file to read")
    parser.add_argument("output", help="Path to write the downloaded contents to")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)

    torrent = open_torrent(args.torrent)
    torrent.download_to_file(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


