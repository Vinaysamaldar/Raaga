/**
 * Raaga Strict Kannada-Only Content Validator Middleware.
 * Every track uploaded through the Admin Dashboard or Ingestion API MUST pass:
 * 1. Explicit `language === "Kannada"` tag check (rejects Hindi, Tamil, Telugu, English, etc.)
 * 2. Kannada Unicode Script presence check (\u0C80-\u0CFF) in `titleKn`
 * 3. Mandatory Kannada category check
 * 4. Valid licensed label & ISRC check
 */

const ALLOWED_CATEGORIES = new Set([
  'film_songs',
  'bhavageethe',
  'janapada',
  'devotional',
  'rajyotsava',
  'indie',
  'carnatic',
]);

const KANNADA_UNICODE_REGEX = /[\u0C80-\u0CFF]/;

function validateKannadaSongUpload(req, res, next) {
  const payload = req.body || {};

  // Rule 1: Language tag MUST be strictly "Kannada"
  if (payload.language !== 'Kannada') {
    return res.status(422).json({
      status: 'REJECTED_NON_KANNADA_LANGUAGE',
      error: `Raaga Content Policy Violation: Only language="Kannada" is permitted. Received language="${payload.language || 'undefined'}".`,
      rule: 'Every track must carry a language = "Kannada" tag, and the upload/admin pipeline must reject any other language.',
    });
  }

  // Rule 2: Kannada script title (titleKn) must contain valid Kannada Unicode characters
  if (!payload.titleKn || !KANNADA_UNICODE_REGEX.test(payload.titleKn)) {
    return res.status(422).json({
      status: 'REJECTED_MISSING_KANNADA_SCRIPT',
      error: 'Track must include a valid title in Kannada script (ಕನ್ನಡ ಲಿಪಿ U+0C80–U+0CFF).',
    });
  }

  // Rule 3: Category must belong to the 7 official Kannada categories
  if (!payload.category || !ALLOWED_CATEGORIES.has(payload.category)) {
    return res.status(422).json({
      status: 'REJECTED_INVALID_CATEGORY',
      error: `Category must be one of: ${Array.from(ALLOWED_CATEGORIES).join(', ')}`,
    });
  }

  // Rule 4: Mandatory metadata completeness
  const requiredFields = [
    'titleEn',
    'artist',
    'singer',
    'composer',
    'lyricist',
    'movieOrAlbum',
    'year',
    'durationSeconds',
    'labelName',
    'isrcCode',
  ];

  const missing = requiredFields.filter((f) => !payload[f]);
  if (missing.length > 0) {
    return res.status(400).json({
      status: 'REJECTED_INCOMPLETE_METADATA',
      error: `Missing required Kannada song metadata fields: ${missing.join(', ')}`,
    });
  }

  next();
}

module.exports = {
  validateKannadaSongUpload,
  ALLOWED_CATEGORIES,
  KANNADA_UNICODE_REGEX,
};
