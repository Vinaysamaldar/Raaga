# Kannada Raaga — Material You Style Guide & Component Library

## 1. Visual Language & Color Tokens
| Token | Hex | Role |
|---|---|---|
| `background` | `#0B1110` | Default Material You very dark green-black canvas |
| `backgroundAmoled` | `#000000` | Optional pitch-black AMOLED power-saving canvas |
| `backgroundLight` | `#F3F7F5` | Optional tonal mint-white light mode canvas |
| `surface / card / chip` | `#18211F` | Slightly lighter charcoal tonal surface (flat, no heavy shadows) |
| `surfaceElevated` | `#212D2A` | Active card / floating mini-player container |
| `primaryText` | `#E3EAE6` | Off-white primary typography |
| `secondaryText` | `#8A9490` | Muted grey subtitles, kickers, and metadata |
| `accentMint` | `#DDE6E1` | Soft pale mint-white for main Play button, `+` FAB, and 160px Recognize circle |
| `accentSaffron` | `#F2A900` | Kannada saffron highlight for active chips, progress rings, and liked heart |

---

## 2. Typography & Geometry
- **English Typeface**: `Montserrat` (weights: 400, 500, 600, 700, 800)
- **Kannada Typeface**: `Noto Sans Kannada` (generous `1.45` line-height so ottaksharas never clip)
- **Hierarchy**:
  - **Screen Title**: `28px` Extra-Bold (`#E3EAE6`)
  - **Section Kicker**: `10.5px` Bold Uppercase (`#8A9490`, letter-spacing `0.9px`)
  - **Section Title**: `17px` Bold (`#E3EAE6`)
  - **Card / Song Title**: `13.5px` Bold (`#E3EAE6`)
  - **Subtitles / Credits**: `11.5px` Medium (`#8A9490`)
- **Corner Radii**:
  - Cards & Tiles: `20px`
  - Song Row Thumbnails: `16px` (`56×56px`)
  - Chips, Floating Mini-Player, Floating Bottom Nav, Primary Buttons: `999px` (Full Pill / Stadium)

---

## 3. Component Library Specifications

### 3.1 Floating Mini-Player Pill
- **Dimensions**: `height: 62px`, `margin: 0 12px`, floating at `bottom: 82px`, `border-radius: 999px`, `background: #212D2A`.
- **Left**: `46×46px` SVG circular progress ring (`stroke: #F2A900`) wrapping a `36×36px` circular album art badge.
- **Center**: Bold single-line song title (Kannada + transliteration) with fading ellipsis + grey artist/movie subtitle.
- **Right**: Previous (`⏮`), `42×42px` circular mint-white (`#DDE6E1`) Play/Pause button with dark icon (`#0B1110`), Next (`⏭`).

### 3.2 Morphing Floating Bottom Navigation Pill
- **Dimensions**: `height: 56px`, `margin: 0 14px`, floating at `bottom: 18px` above the Android gesture bar, `border-radius: 999px`, `background: #141C1A`.
- **5 Items**: `Home`, `Search`, `Recognize` (mic), `Library`, `More` (`•••`).
- **Behavior**: Active item expands smoothly (`cubic-bezier(0.2, 0.8, 0.2, 1)`) into a lighter pill (`#2A3835`) showing **Icon + Label**; inactive items show **Icons only**.

### 3.3 Song Row Component (`56px`)
- **Thumbnail**: `56×56px`, `16px` radius, displays Kannada initial + release year.
- **Body**: Bold Kannada title (`#E3EAE6`), English transliteration (`#DDE6E1`), muted grey artist & movie (`#8A9490`).
- **Playing State**: Animated 3-bar saffron equalizer (`eqBounce`) next to the title.
- **Trailing**: Circular mint-white/saffron Play/Pause button, Download status icon (not downloaded `⬇`, progress ring `◔`, completed check `✓`), and 3-dot menu (`⋮`).

### 3.4 Library 2-Column Tonal Tiles
- `20px` rounded charcoal cards (`#18211F`), `34×34px` rounded icon container on the left, bold title + count subtitle on the right.
- Includes: `Liked`, `Downloaded`, `Exported`, `Cached`, `My Top 50`, `My Bottom 50`, `Local`, `Favorites A–Z`, and `Bhavageethe`.

### 3.5 Recognize Music 160px Mint Button
- `160×160px` circular `#DDE6E1` button with dark `🎵` icon and 3 concentric expanding ripple rings (`@keyframes rippleOut`) during acoustic fingerprinting.
