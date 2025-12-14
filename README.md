# torrent-client (Python)

Tiny BitTorrent client rewritten in Python 3. It mirrors the behaviour of the
original Go implementation described in https://blog.jse.li/posts/torrent/.

## Requirements

- Python 3.11+
- Ability to open outbound TCP connections to trackers/peers

## Usage

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip

python main.py debian-13.2.0-amd64-netinst.iso.torrent debian.iso
```

Logging is verbose/colorful by default. Pass `-q/--quiet` to reduce output.

## Tests

```sh
python -m unittest discover -s tests
```

## Limitations

- Only supports `.torrent` files (no magnet links)
- Only supports HTTP trackers that return compact peer lists
- Single-file torrents only
- Download-only (does not upload pieces to peers)
