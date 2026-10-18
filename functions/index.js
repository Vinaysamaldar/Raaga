/**
 * Ragaa Cloud Functions for Passwordless Email Code Authentication
 * 
 * Strict Security Rules:
 * - Codes are stored only as SHA-256 hashes with HMAC salt.
 * - Single-use codes that expire in 10 minutes.
 * - Rate limiting: 30s resend cooldown, max 5 sends per hour per email.
 * - Brute force protection: max 5 wrong attempts before a 15-minute lockout.
 * - Raw codes and plaintext email addresses are never written to server logs.
 */

const { onCall, HttpsError } = require("firebase-functions/v2/https");
const admin = require("firebase-admin");
const crypto = require("crypto");

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

// Server-side secret salt for hashing codes
const AUTH_SECRET = process.env.RAGAA_AUTH_SECRET || "ragaa_kannada_swara_default_secret_2026";

/**
 * Hash code with email and secret
 */
function hashCode(email, code) {
  return crypto
    .createHmac("sha256", AUTH_SECRET)
    .update(`${email.toLowerCase().trim()}:${code}`)
    .digest("hex");
}

/**
 * Mask email for logging (e.g. v***@example.com)
 */
function maskEmail(email) {
  const parts = email.split("@");
  if (parts.length < 2) return "***";
  const user = parts[0];
  const domain = parts[1];
  return `${user.charAt(0)}***@${domain}`;
}

/**
 * Callable Function 1: requestEmailCode
 */
exports.requestEmailCode = onCall({ cors: true, maxInstances: 10 }, async (request) => {
  const { email } = request.data || {};
  if (!email || typeof email !== "string") {
    throw new HttpsError("invalid-argument", "Valid email address is required.");
  }

  const cleanEmail = email.toLowerCase().trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(cleanEmail)) {
    throw new HttpsError("invalid-argument", "Invalid email format.");
  }

  const emailDocId = crypto.createHash("sha256").update(cleanEmail).digest("hex");
  const codeRef = db.collection("ragaa_email_codes").doc(emailDocId);
  const now = Date.now();

  const doc = await codeRef.get();
  if (doc.exists) {
    const data = doc.data();

    // 1. Lockout check (5 wrong attempts -> 15 min lock)
    if (data.lockedUntil && now < data.lockedUntil) {
      const waitMin = Math.ceil((data.lockedUntil - now) / 60000);
      throw new HttpsError(
        "resource-exhausted",
        `Too many failed attempts. Locked for ${waitMin} more minute(s).`
      );
    }

    // 2. Resend Cooldown (30 seconds)
    if (data.lastSentAt && now - data.lastSentAt < 30 * 1000) {
      const secondsLeft = Math.ceil((30 * 1000 - (now - data.lastSentAt)) / 1000);
      throw new HttpsError(
        "resource-exhausted",
        `Please wait ${secondsLeft}s before requesting a new code.`
      );
    }

    // 3. Hourly limit (Max 5 sends per hour)
    const hourAgo = now - 60 * 60 * 1000;
    const recentSends = (data.sendTimestamps || []).filter((t) => t > hourAgo);
    if (recentSends.length >= 5) {
      throw new HttpsError(
        "resource-exhausted",
        "Hourly code request limit reached. Please try again later."
      );
    }
  }

  // Generate cryptographically secure 6-digit code (100000 - 999999)
  const codeInt = crypto.randomInt(100000, 1000000);
  const codeStr = String(codeInt);
  const hashed = hashCode(cleanEmail, codeStr);

  const expiresAt = now + 10 * 60 * 1000; // 10 minutes
  const existingSends = doc.exists ? doc.data().sendTimestamps || [] : [];
  const hourAgo = now - 60 * 60 * 1000;
  const updatedSends = [...existingSends.filter((t) => t > hourAgo), now];

  await codeRef.set(
    {
      codeHash: hashed,
      createdAt: now,
      lastSentAt: now,
      expiresAt: expiresAt,
      attemptsCount: 0,
      used: false,
      sendTimestamps: updatedSends,
      lockedUntil: null
    },
    { merge: true }
  );

  // In production, integrate SendGrid / Postmark / Firebase Extension:
  // await sendTransactionalEmail(cleanEmail, codeStr);
  // Security guarantee: we log only masked identifier, never raw code or full email.
  console.log(`[Ragaa Auth] Verification code issued for ${maskEmail(cleanEmail)}`);

  return {
    success: true,
    expiresInSeconds: 600,
    maskedEmail: maskEmail(cleanEmail)
  };
});

/**
 * Callable Function 2: verifyEmailCode
 */
exports.verifyEmailCode = onCall({ cors: true, maxInstances: 10 }, async (request) => {
  const { email, code } = request.data || {};
  if (!email || !code) {
    throw new HttpsError("invalid-argument", "Email and 6-digit code are required.");
  }

  const cleanEmail = email.toLowerCase().trim();
  const cleanCode = String(code).trim();
  if (cleanCode.length !== 6 || !/^\d{6}$/.test(cleanCode)) {
    throw new HttpsError("invalid-argument", "Verification code must be 6 digits.");
  }

  const emailDocId = crypto.createHash("sha256").update(cleanEmail).digest("hex");
  const codeRef = db.collection("ragaa_email_codes").doc(emailDocId);
  const now = Date.now();

  const doc = await codeRef.get();
  if (!doc.exists) {
    throw new HttpsError("not-found", "No active verification code found for this email.");
  }

  const data = doc.data();

  // 1. Check if locked
  if (data.lockedUntil && now < data.lockedUntil) {
    const waitMin = Math.ceil((data.lockedUntil - now) / 60000);
    throw new HttpsError(
      "permission-denied",
      `Too many failed attempts. Account is locked for ${waitMin} minute(s).`
    );
  }

  // 2. Check if already used
  if (data.used) {
    throw new HttpsError(
      "failed-precondition",
      "This code has already been used. Please request a new code."
    );
  }

  // 3. Check expiration
  if (now > data.expiresAt) {
    throw new HttpsError(
      "deadline-exceeded",
      "Verification code has expired. Please request a new code."
    );
  }

  // 4. Verify code hash
  const inputHash = hashCode(cleanEmail, cleanCode);
  const isMatch = crypto.timingSafeEqual(
    Buffer.from(inputHash, "utf8"),
    Buffer.from(data.codeHash, "utf8")
  );

  if (!isMatch) {
    const newAttempts = (data.attemptsCount || 0) + 1;
    const remaining = 5 - newAttempts;

    if (newAttempts >= 5) {
      // Lock for 15 minutes
      const lockTime = now + 15 * 60 * 1000;
      await codeRef.update({
        attemptsCount: newAttempts,
        lockedUntil: lockTime
      });
      throw new HttpsError(
        "permission-denied",
        "Incorrect code. Maximum attempts reached. Locked for 15 minutes."
      );
    } else {
      await codeRef.update({ attemptsCount: newAttempts });
      throw new HttpsError(
        "invalid-argument",
        `Incorrect code. ${remaining} attempt${remaining === 1 ? "" : "s"} left.`
      );
    }
  }

  // 5. Code is valid! Mark as used immediately (single-use guarantee)
  await codeRef.update({ used: true, attemptsCount: 0, lockedUntil: null });

  // 6. Get or create Firebase user
  let userRecord;
  let isNewUser = false;
  try {
    userRecord = await admin.auth().getUserByEmail(cleanEmail);
  } catch (err) {
    if (err.code === "auth/user-not-found") {
      userRecord = await admin.auth().createUser({
        email: cleanEmail,
        emailVerified: true,
        displayName: cleanEmail.split("@")[0]
      });
      isNewUser = true;
    } else {
      throw new HttpsError("internal", "Authentication verification error.");
    }
  }

  // 7. Mint custom token
  const customToken = await admin.auth().createCustomToken(userRecord.uid, {
    email: cleanEmail,
    provider: "email-code"
  });

  console.log(`[Ragaa Auth] Successful verification for ${maskEmail(cleanEmail)} (isNewUser: ${isNewUser})`);

  return {
    success: true,
    customToken: customToken,
    isNewUser: isNewUser,
    uid: userRecord.uid,
    email: cleanEmail,
    displayName: userRecord.displayName || cleanEmail.split("@")[0]
  };
});
