# Raaga (ರಾಗ) — REST API Documentation

Base URL: `https://api.raaga.karnataka.in/api/v1`

---

## 1. Content Policy Enforcement Rule
Every ingestion endpoint strictly enforces:
- `language === "Kannada"` (case-sensitive)
- `titleKn` contains Unicode characters in the Kannada block (`U+0C80`–`U+0CFF`)
- `category` is one of: `film_songs`, `bhavageethe`, `janapada`, `devotional`, `rajyotsava`, `indie`, `carnatic`.

---

## 2. Endpoints

### 2.1 Alphabetical A-to-Z Browse (`ಅ–ಳ` & `A–Z`)
`GET /songs/browse-az`

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `script` | `string` | `kn` | `kn` for Kannada Varnamale (`ಅ–ಳ`), `en` for English (`A–Z`) |
| `letter` | `string` | *(optional)* | Specific letter (e.g., `ಅ`, `ಕ`, `ಹ`, or `A`, `K`, `H`) |
| `sort` | `string` | `title` | `title`, `year`, or `popularity` |
| `category` | `string` | *(optional)* | Filter by one of the 7 Kannada categories |

**Response (`200 OK`):**
```json
{
  "languagePolicy": "Kannada Only",
  "script": "kn",
  "letter": "ಹ",
  "count": 1,
  "songs": [
    {
      "id": "kn_001",
      "titleKn": "ಹುಟ್ಟಿದರೆ ಕನ್ನಡ ನಾಡಲ್ಲಿ ಹುಟ್ಟಬೇಕು",
      "titleEn": "Huttidare Kannada Naadalli Huttabeku",
      "kannadaInitial": "ಹ",
      "englishInitial": "H",
      "artist": "Dr. Rajkumar",
      "singer": "Dr. Rajkumar",
      "composer": "Hamsalekha",
      "lyricist": "Hamsalekha",
      "movieOrAlbum": "Akasmika",
      "year": 1993,
      "category": "rajyotsava",
      "durationSeconds": 284,
      "language": "Kannada",
      "labelName": "Lahari Music",
      "isrcCode": "IN-LAH-93-00101"
    }
  ]
}
```

---

### 2.2 Kannada Script & Transliteration Search
`GET /songs/search?q={query}`

Supports queries in Kannada script (`ಮುಂಗಾರು`), English (`Mungaru Male`), or phonetic transliteration with typo tolerance (`Mungru`).

---

### 2.3 Admin Song Upload & Kannada Validation Pipeline
`POST /admin/songs/upload`

**Request Body:**
```json
{
  "titleKn": "ಕಾಣದ ಕಡಲಿಗೆ ಹಂಬಲಿಸಿದೆ ಮನ",
  "titleEn": "Kaanada Kadalige Hambaliside Mana",
  "language": "Kannada",
  "category": "bhavageethe",
  "artist": "C. Ashwath",
  "singer": "C. Ashwath",
  "composer": "C. Ashwath",
  "lyricist": "Dr. G. S. Shivarudrappa",
  "movieOrAlbum": "Kaanada Kadalige",
  "year": 1986,
  "durationSeconds": 295,
  "labelName": "Lahari Music",
  "isrcCode": "IN-LAH-86-00912"
}
```

**Error Response when `language != "Kannada"` (`422 Unprocessable Entity`):**
```json
{
  "status": "REJECTED_NON_KANNADA_LANGUAGE",
  "error": "Raaga Content Policy Violation: Only language=\"Kannada\" is permitted. Received language=\"Hindi\".",
  "rule": "Every track must carry a language = \"Kannada\" tag, and the upload/admin pipeline must reject any other language."
}
```

---

### 2.4 Offline AES-256 Encryption License Exchange
`POST /offline/license-key`

Issues a device-bound AES-256-CBC key and IV stored in Android Keystore / iOS Keychain via `flutter_secure_storage` so downloaded tracks are playable **only** inside the Raaga app.

---

### 2.5 Royalty Stream Event Logging
`POST /royalties/stream-event`

Records qualified streams ($\ge 30$ seconds) and offline plays against the track's `isrcCode` and `labelName` for monthly royalty settlement with Anand Audio, Lahari Music, Saregama, Aditya Music, PRK Audio, and Jhankar Music.

---

### 2.6 Copyright Takedown Submission
`POST /legal/takedown`

Creates a priority takedown review ticket (`#TD-KA-*`) compliant with the Indian Copyright Act 1957 and DMCA.
