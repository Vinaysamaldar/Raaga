# Kannada Open Music Collector

Builds a catalog of **openly licensed** Kannada audio for the Kannada Raaga app and,
if you ask, downloads it. It uses only the official public APIs of:

| Source | Notes |
|---|---|
| Internet Archive | Old devotional, folk and Dasa Sahitya recordings. Per-item license check. |
| Wikimedia Commons | Free-licensed audio clips. Requires attribution. |
| Jamendo | Independent artists. Needs a free `JAMENDO_CLIENT_ID`. |
| Openverse | Aggregator over many Creative Commons collections. |

## Setup

```bash
pip install -r requirements.txt
export JAMENDO_CLIENT_ID=your_id     # optional, from devportal.jamendo.com
```

## Usage

```bash
python kannada_open_collector.py --self-test            # offline sanity check
python kannada_open_collector.py                        # build catalog only
python kannada_open_collector.py --download             # also download audio
python kannada_open_collector.py --sources archive,commons --limit 500 --download
```

Useful flags: `--strict` (Kannada must appear in title, tags or language, not just
the description), `--max-downloads N`, `--max-size-mb N`, `--delay SECONDS`.

## License policy

Default keeps only: **CC0, Public Domain, CC BY, CC BY-SA**.

- `--allow-nc` adds NonCommercial licenses. Do **not** use for a monetized app.
- `--allow-nd` adds NoDerivatives licenses. Re-encoding or trimming may count as a change, so be careful.
- BY-SA tracks carry share-alike terms, and every CC BY or BY-SA track needs visible credit
  (see `ATTRIBUTION.md`).
- "Public domain" labels from Archive.org uploaders are claims, not guarantees. Rows
  with a `review_note` should be checked by hand before you ship them.
- Jamendo's API terms may require approval for commercial apps. Check them first.

This is not legal advice. Have someone qualified review your licensing before launch.

## Output (`kannada_open_catalog/`)

- `catalog.csv` / `catalog.json`: accepted tracks (CSV opens in Excel with Kannada text intact)
- `rejected.csv`: everything filtered out and the reason
- `az_index.json`: Kannada letters and English A-Z mapped to track ids, ready for the app's A to Z screen
- `ATTRIBUTION.md`: credits to show in the app
- `audio/`: downloaded files (only with `--download`)

## What to expect

The open catalog is small, mostly devotional, folk, classical and independent music.
Mainstream Kannada film songs are not openly licensed and will not appear. Growing
beyond this needs licensing deals with the labels.
