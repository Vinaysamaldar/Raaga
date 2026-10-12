-- ============================================================================
-- RAAGA: EXCLUSIVE KANNADA MUSIC STREAMING PLATFORM
-- PostgreSQL Database Schema + Kannada Full-Text Search & Royalty Ledger
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 1. Mandatory Kannada Music Categories Enum
CREATE TYPE kannada_category AS ENUM (
    'film_songs',        -- Kannada Film Songs (Old classics to latest)
    'bhavageethe',       -- Bhavageethe
    'janapada',          -- Folk (Janapada)
    'devotional',        -- Devotional (Dasa Sahitya, Vachanas, Bhajans)
    'rajyotsava',        -- Rajyotsava / Patriotic songs
    'indie',             -- Kannada Indie and Albums
    'carnatic'           -- Kannada Devotional / Classical (Carnatic)
);

-- 2. Licensed Music Labels & Rights Holders (Anand Audio, Lahari, Saregama, etc.)
CREATE TABLE music_labels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL UNIQUE,
    name_kn VARCHAR(150),
    license_agreement_code VARCHAR(80) NOT NULL UNIQUE,
    royalty_rate_per_stream_inr NUMERIC(8, 4) NOT NULL DEFAULT 0.1200,
    contract_valid_until DATE NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Artists / Singers / Composers / Lyricists
CREATE TABLE artists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_kn VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    kannada_initial VARCHAR(4) NOT NULL,
    english_initial CHAR(1) NOT NULL,
    bio_kn TEXT,
    bio_en TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Movies & Albums
CREATE TABLE movies_or_albums (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_kn VARCHAR(250) NOT NULL,
    title_en VARCHAR(250) NOT NULL,
    kannada_initial VARCHAR(4) NOT NULL,
    english_initial CHAR(1) NOT NULL,
    release_year INT NOT NULL CHECK (release_year BETWEEN 1934 AND 2100),
    is_movie BOOLEAN NOT NULL DEFAULT TRUE,
    cover_art_url TEXT NOT NULL,
    label_id UUID NOT NULL REFERENCES music_labels(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Songs Catalog (STRICT KANNADA-ONLY ENFORCEMENT AT DATABASE LEVEL)
CREATE TABLE songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    isrc_code VARCHAR(32) NOT NULL UNIQUE,
    title_kn VARCHAR(255) NOT NULL,
    title_en VARCHAR(255) NOT NULL,
    -- Alphabetical A-to-Z Browsing Columns (ಅ–ಳ and A–Z)
    kannada_initial VARCHAR(4) NOT NULL,
    english_initial CHAR(1) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    singer_name VARCHAR(255) NOT NULL,
    composer_name VARCHAR(255) NOT NULL,
    lyricist_name VARCHAR(255) NOT NULL,
    movie_or_album_id UUID REFERENCES movies_or_albums(id),
    movie_or_album_title VARCHAR(255) NOT NULL,
    release_year INT NOT NULL CHECK (release_year BETWEEN 1934 AND 2100),
    category kannada_category NOT NULL,
    genre VARCHAR(120) NOT NULL,
    duration_seconds INT NOT NULL CHECK (duration_seconds > 0),
    cover_art_url TEXT NOT NULL,

    -- HARD CONTENT RULE: ONLY KANNADA SONGS ALLOWED
    language VARCHAR(32) NOT NULL DEFAULT 'Kannada'
        CONSTRAINT chk_exclusively_kannada_language CHECK (language = 'Kannada'),

    -- Ensure title_kn contains genuine Kannada Unicode characters (U+0C80..U+0CFF)
    CONSTRAINT chk_title_kn_unicode CHECK (title_kn ~ '[\u0C80-\u0CFF]'),

    -- Adaptive Bitrate CDN HLS Endpoints
    hls_low_64k_url TEXT NOT NULL,
    hls_med_128k_url TEXT NOT NULL,
    hls_high_320k_url TEXT NOT NULL,

    -- Licensing & Popularity
    label_id UUID NOT NULL REFERENCES music_labels(id),
    popularity_score INT NOT NULL DEFAULT 50 CHECK (popularity_score BETWEEN 0 AND 100),
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Time-Synced Lyrics (Kannada Script + English Transliteration)
CREATE TABLE song_synced_lyrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    timestamp_ms INT NOT NULL CHECK (timestamp_ms >= 0),
    kannada_line TEXT NOT NULL,
    english_transliteration TEXT NOT NULL,
    UNIQUE (song_id, timestamp_ms)
);

-- 7. Users, Favorites, Custom Playlists & Cross-Device Listening History
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(24) UNIQUE,
    google_email VARCHAR(255) UNIQUE,
    display_name VARCHAR(150) NOT NULL,
    preferred_ui_language CHAR(2) NOT NULL DEFAULT 'kn' CHECK (preferred_ui_language IN ('kn', 'en')),
    preferred_quality VARCHAR(16) NOT NULL DEFAULT 'medium128k',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_favorites (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, song_id)
);

CREATE TABLE playlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title_kn VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    is_editorial_mood BOOLEAN NOT NULL DEFAULT FALSE,
    mood_tag VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE playlist_songs (
    playlist_id UUID NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    position INT NOT NULL,
    PRIMARY KEY (playlist_id, song_id)
);

CREATE TABLE listening_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    played_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    listened_seconds INT NOT NULL,
    was_offline_playback BOOLEAN NOT NULL DEFAULT FALSE
);

-- 8. Royalty Reporting Ledger & Copyright Takedowns
CREATE TABLE royalty_ledger (
    id BIGSERIAL PRIMARY KEY,
    song_id UUID NOT NULL REFERENCES songs(id),
    label_id UUID NOT NULL REFERENCES music_labels(id),
    stream_month CHAR(7) NOT NULL, -- YYYY-MM
    qualified_online_streams BIGINT NOT NULL DEFAULT 0,
    qualified_offline_plays BIGINT NOT NULL DEFAULT 0,
    total_royalty_payable_inr NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    UNIQUE (song_id, stream_month)
);

CREATE TABLE copyright_takedowns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_id UUID REFERENCES songs(id),
    claimed_work_title VARCHAR(255) NOT NULL,
    claimant_name VARCHAR(200) NOT NULL,
    claimant_email VARCHAR(255) NOT NULL,
    evidence_url TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_REVIEW',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- KANNADA-AWARE INDEXES FOR A-TO-Z BROWSING & TYPO-TOLERANT FULL-TEXT SEARCH
-- ============================================================================

-- Fast A-to-Z Browsing by Kannada Varnamale (ಅ–ಳ) and English (A–Z)
CREATE INDEX idx_songs_kannada_initial ON songs (kannada_initial, title_kn, release_year, popularity_score DESC);
CREATE INDEX idx_songs_english_initial ON songs (english_initial, title_en, release_year, popularity_score DESC);
CREATE INDEX idx_songs_category ON songs (category, popularity_score DESC);

-- Trigram indexes for typo-tolerant search across Kannada script & English transliteration
CREATE INDEX idx_songs_trgm_title_kn ON songs USING gin (title_kn gin_trgm_ops);
CREATE INDEX idx_songs_trgm_title_en ON songs USING gin (title_en gin_trgm_ops);
CREATE INDEX idx_songs_trgm_metadata ON songs USING gin (
    (artist_name || ' ' || singer_name || ' ' || composer_name || ' ' || lyricist_name || ' ' || movie_or_album_title) gin_trgm_ops
);
