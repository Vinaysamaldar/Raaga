# Kannada Raaga (ಕನ್ನಡ ರಾಗ)

**Kannada Raaga** is a Material You (`390×844` Android-first) Kannada music streaming application and open heritage collector dedicated exclusively to Kannada music (1934–2026).

---

## 4-Pillar Kannada Music Heritage Archive (200,000+ Track Catalog)

1. **🎬 Sandalwood Film Songs (1934–2026)**: 25,000+ film songs across 5,000+ Kannada films — from Golden Era classics (*Bedara Kannappa*, *Bangarada Manushya*, *Kasturi Nivasa*, *Naagarahaavu*, *Gandhada Gudi*, *Premaloka*, *Amruthavarshini*, *Om*) to modern blockbusters (*Mungaru Male*, *Raajakumara*, *KGF 1 & 2*, *Kantara*, *Sapta Sagaradaache Ello*, *Krishnam Pranaya Sakhi*, *Kaatera*, *Toxic*).
2. **🪔 Devotional, Dasa Sahitya, Vachanas & Carnatic**: *Purandara Dasa* & *Kanaka Dasa* Keerthanegalu, *Basavanna* & *Akka Mahadevi* Vachanas, Carnatic kritis, and Karnataka temple devotional recordings.
3. **🥁 Folk & Traditional (`Janapada Geethegalu` & `Bhavageethe`)**: Karnataka oral folk traditions, *Kolata*, *Kamsale*, *Shishunala Sharif* Tatvapada, and Rashtrakavi *Kuvempu*, *D. R. Bendre*, *K. S. Narasimhaswamy*, and *C. Ashwath* Bhavageethe.
4. **🎸 Modern Independent, Pop, Rap & Rock**: *The Raghu Dixit Project*, *Vasu Dixit*, *Swarathma*, Kannada Rap/Hip-Hop (*Chandan Shetty*, *All OK*, *Rahul Dit-O*), and independent Kannada pop singles.

---

## Kannada Open Music Collector (`kannada_open_collector.py`)

Builds an **openly licensed** catalog of Kannada audio for the Kannada Raaga app and downloads audio streams from official public APIs:

| Source | Notes |
|---|---|
| **Internet Archive** | Historical devotional, folk, and Dasa Sahitya recordings. Per-item license check. |
| **Wikimedia Commons** | Free-licensed Kannada speech, folk, and musical clips. Direct streaming audio. |
| **Openverse** | Aggregator over Creative Commons cultural collections. |
| **Jamendo** | Independent Kannada indie/folk artists. Needs a free `JAMENDO_CLIENT_ID`. |

### Setup & Requirements

```bash
pip install -r requirements.txt
export JAMENDO_CLIENT_ID=your_id     # optional, from devportal.jamendo.com
```

Dependencies in `requirements.txt`:
- `requests>=2.31.0`
- `indic-transliteration>=2.3.0`

### Usage

```bash
# 1. Offline sanity self-test
python kannada_open_collector.py --self-test

# 2. Build open catalog without downloading heavy audio files
python kannada_open_collector.py --sources commons,openverse --limit 200

# 3. Download audio files locally
python kannada_open_collector.py --download --max-downloads 50
```

### Collector Output (`kannada_open_catalog/`)

- `catalog.json` / `catalog.csv`: Accepted openly licensed Kannada tracks with direct audio URLs, Kannada script title, transliterated title, artist, source, and license.
- `rejected.csv`: Filtered entries and rejection reason (e.g. invalid license, non-audio).
- `az_index.json`: A–Z mapping for Kannada script (ಅ-ಳ) and English alphabet.
- `ATTRIBUTION.md`: Full legal attribution text with license requirements.
- `audio/`: Downloaded `.ogg`, `.mp3`, or `.wav` files (when `--download` is passed).

### License Policy

The collector strictly retains only permissive open licenses:
- **CC0 (Public Domain Dedication)**
- **Public Domain (PD)**
- **CC BY (Attribution)**
- **CC BY-SA (ShareAlike)**

Flag options:
- `--allow-nc`: Include NonCommercial licenses (do not use for commercial deployments).
- `--allow-nd`: Include NoDerivatives licenses.

---

## App Features

- **Material You Mobile Design**: Designed for Android viewport `390×844` with adaptive dark (#0B1110), AMOLED (#000000), and Light tonal themes.
- **Accurate Audio Seeking**: HTML5 audio streaming with precise scrubber tracking, progress bar, and zero restart bug.
- **Open Licensed (CC/PD) Sub-Archive**: Dedicated filter chip and search tab connecting directly to the open catalog.
- **In-App Attribution Viewer**: Legal modal accessible under the "More" screen detailing all CC and Public Domain licenses.
- **Bilingual A–Z Index**: Browse by Kannada alphabet (ಅ, ಆ, ಇ... ಕ, ಖ, ಗ...) or English (A–Z).
- **Vercel Deployment Ready**: Configured for static deployment without 404s via root and mobile mirrors.

---

## Running Locally

```bash
python serve_raaga.py
```
Open in browser:
- `http://localhost:8090/mobile/web_preview/index.html` or `http://localhost:8090/index.html`
