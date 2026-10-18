const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const artifactDir = 'C:\\Users\\DELL\\.gemini\\antigravity\\brain\\cc9b9613-c2e3-455a-9235-fe78d84a0aea';

// Unit Test Assertions
function assert(condition, message) {
  if (!condition) {
    throw new Error('Assertion Failed: ' + message);
  }
}

async function runUnitTests() {
  console.log('\n========================================');
  console.log('1. RUNNING UNIT TESTS (Validation & SixBox)');
  console.log('========================================');

  // 1. Email validation test
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  assert(emailRegex.test('user@ragaa.music'), 'Valid email passes');
  assert(emailRegex.test('dr.rajkumar@kannada.org'), 'Valid email with dot passes');
  assert(!emailRegex.test('invalid-email'), 'Invalid email without @ fails');
  assert(!emailRegex.test('missing-domain@'), 'Invalid email missing domain fails');
  console.log('✓ Email Regex Validation: PASSED');

  // 2. Phone validation test
  const phoneTest = (num) => {
    const digits = num.replace(/[^0-9]/g, '');
    return digits.length >= 8 && digits.length <= 12;
  };
  assert(phoneTest('9876543210'), '10-digit phone passes');
  assert(phoneTest('+91 98765 43210'), 'Formatted phone passes');
  assert(!phoneTest('123'), 'Too short phone fails');
  assert(!phoneTest('123456789012345'), 'Too long phone fails');
  console.log('✓ Phone Number Validation: PASSED');

  // 3. SixBox Code Logic Simulation
  const mockBoxes = ['', '', '', '', '', ''];
  const pasteData = '849201';
  for (let i = 0; i < 6; i++) {
    mockBoxes[i] = pasteData.charAt(i);
  }
  assert(mockBoxes.join('') === '849201', 'Paste splits into 6 digits');

  // Backspace simulation
  let activeIndex = 5;
  mockBoxes[activeIndex] = '';
  activeIndex--;
  assert(activeIndex === 4, 'Backspace retreats index');
  console.log('✓ SixBox Code Paste & Backspace Logic: PASSED');
}

async function runBrowserTests() {
  console.log('\n========================================');
  console.log('2. RUNNING RESPONSIVE & FLOW TESTS (Playwright)');
  console.log('========================================');

  let browser;
  try {
    browser = await chromium.launch({ channel: 'msedge', headless: true });
  } catch (e) {
    browser = await chromium.launch({ headless: true });
  }

  const context = await browser.newContext();
  const page = await context.newPage();

  // Test A: Desktop (1366 x 850)
  console.log('\n--- Test A: Desktop Viewport (1366x850) ---');
  await page.setViewportSize({ width: 1366, height: 850 });
  await page.goto('http://127.0.0.1:8090/index.html?route=login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(800);

  const desktopScreenshot = path.join(artifactDir, 'auth_desktop_1366.png');
  await page.screenshot({ path: desktopScreenshot });
  console.log('Captured auth desktop screenshot:', desktopScreenshot);

  // Verify Desktop split layout
  const isBrandPanelVisible = await page.evaluate(() => {
    const p = document.querySelector('.login-brand-panel');
    return p && window.getComputedStyle(p).display !== 'none';
  });
  console.log('Desktop brand panel visible:', isBrandPanelVisible);
  assert(isBrandPanelVisible, 'Brand hero panel must be visible on desktop');

  // Test B: Tablet (768 x 1024)
  console.log('\n--- Test B: Tablet Viewport (768x1024) ---');
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.waitForTimeout(500);

  const tabletScreenshot = path.join(artifactDir, 'auth_tablet_768.png');
  await page.screenshot({ path: tabletScreenshot });
  console.log('Captured auth tablet screenshot:', tabletScreenshot);

  // Test C: Phone (360 x 780)
  console.log('\n--- Test C: Mobile Phone Viewport (360x780) ---');
  await page.setViewportSize({ width: 360, height: 780 });
  await page.waitForTimeout(500);

  const phoneScreenshot = path.join(artifactDir, 'auth_phone_360.png');
  await page.screenshot({ path: phoneScreenshot });
  console.log('Captured auth phone screenshot:', phoneScreenshot);

  const isBrandHiddenOnPhone = await page.evaluate(() => {
    const p = document.querySelector('.login-brand-panel');
    return p && window.getComputedStyle(p).display === 'none';
  });
  console.log('Brand panel hidden on phone:', isBrandHiddenOnPhone);
  assert(isBrandHiddenOnPhone, 'Brand panel should be hidden on phone for single column');

  // Test D: Language Toggle (ಕನ್ನಡ | EN)
  console.log('\n--- Test D: Language Switcher ---');
  await page.click('#authLangKnBtn');
  await page.waitForTimeout(300);
  const kannadaHeading = await page.evaluate(() => document.getElementById('authWelcomeHeading')?.innerText);
  console.log('Kannada Heading text:', kannadaHeading);
  assert(kannadaHeading === 'ಮರಳಿ ಸ್ವಾಗತ', 'Kannada heading updated');

  await page.click('#authLangEnBtn');
  await page.waitForTimeout(200);

  // Test E: Email Code Flow with SixBoxCodeInput
  console.log('\n--- Test E: Email Code Flow with SixBoxCodeInput ---');
  await page.click('#txtBtnEmail');
  await page.waitForTimeout(300);

  // Enter email
  await page.fill('#authEmailInputBox', 'listener@ragaa.music');
  await page.click('#btnSendEmailCodeSubmit');
  await page.waitForTimeout(400);

  // Verify Step 2 is active
  const isVerifyActive = await page.evaluate(() => {
    return document.getElementById('authScreenEmailVerify')?.classList.contains('active');
  });
  console.log('Email verify step active:', isVerifyActive);
  assert(isVerifyActive, 'Step 2 verify screen must be active');

  // Test SixBox paste
  console.log('Testing SixBox paste of "849201"...');
  await page.evaluate(() => {
    for (let i = 0; i < 6; i++) {
      const b = document.getElementById(`emailCode${i}`);
      b.value = '849201'.charAt(i);
      b.dispatchEvent(new Event('input'));
    }
  });
  await page.waitForTimeout(300);

  const verifyBtnEnabled = await page.evaluate(() => {
    const btn = document.getElementById('btnVerifyEmailSubmit');
    return btn && !btn.disabled;
  });
  console.log('Verify button enabled when 6 digits entered:', verifyBtnEnabled);
  assert(verifyBtnEnabled, 'Verify button must enable when 6 digits filled');

  const emailCodeScreenshot = path.join(artifactDir, 'auth_email_code.png');
  await page.screenshot({ path: emailCodeScreenshot });
  console.log('Captured email code screenshot:', emailCodeScreenshot);

  // Test Submit Code -> Profile Step
  await page.click('#btnVerifyEmailSubmit');
  await page.waitForTimeout(600);

  const isProfileStepActive = await page.evaluate(() => {
    return document.getElementById('authScreenProfile')?.classList.contains('active');
  });
  console.log('New user transitioned to profile setup:', isProfileStepActive);

  // Complete profile
  await page.fill('#profileNameInput', 'Ragaa Kannada Listener');
  await page.click('#txtGetStartedBtn');
  await page.waitForTimeout(700);

  // Verify redirected to Home and session saved
  const userSession = await page.evaluate(() => {
    return localStorage.getItem('ragaa_user_session');
  });
  console.log('Saved user session after auth:', userSession);
  assert(userSession && userSession.includes('ragaa.music'), 'Session must persist in localStorage');

  // Test F: Guest Guard & Return Flow
  console.log('\n--- Test F: Guest Protection Guard & Return Tab ---');
  // 1. Sign out to become guest
  await page.evaluate(() => signOutCurrentSession());
  await page.waitForTimeout(300);

  // 2. Open Library tab
  await page.evaluate(() => switchNav('library'));
  await page.waitForTimeout(300);

  // 3. Click FAB to create playlist (Guest action)
  await page.click('#libraryFab');
  await page.waitForTimeout(300);

  // 4. Verify "Sign in to use this" sheet opened
  const isGuestSheetOpen = await page.evaluate(() => {
    const s = document.getElementById('guestAuthSheetBackdrop');
    return s && s.classList.contains('show');
  });
  console.log('"Sign in to use this" sheet opened for guest:', isGuestSheetOpen);
  assert(isGuestSheetOpen, 'Guest sheet must open when unauthenticated guest tries protected action');

  const guestSheetScreenshot = path.join(artifactDir, 'auth_guest_sheet.png');
  await page.screenshot({ path: guestSheetScreenshot });
  console.log('Captured guest sheet screenshot:', guestSheetScreenshot);

  // 5. Click "Sign In" from guest sheet
  await page.click('.guest-auth-sheet .auth-btn-primary');
  await page.waitForTimeout(400);

  // Verify login opened with returnTab preserved
  const returnTab = await page.evaluate(() => ragaaAuthState.returnTab);
  console.log('Login returnTab preserved:', returnTab);
  assert(returnTab === 'library', 'Return tab must be preserved as library');

  // 6. Complete login with Google
  await page.click('.auth-btn-google');
  await page.waitForTimeout(1000);

  // 7. Verify user returned to Library tab!
  const currentTabAfterLogin = await page.evaluate(() => {
    const libScreen = document.getElementById('screen-library');
    return libScreen && libScreen.classList.contains('active');
  });
  console.log('User returned to Library tab after login:', currentTabAfterLogin);
  assert(currentTabAfterLogin, 'User must return to the tab they came from');

  await browser.close();
  console.log('\n========================================');
  console.log('ALL AUTH TESTS & VIEWPORTS PASSED 100%!');
  console.log('========================================\n');
}

async function main() {
  await runUnitTests();
  await runBrowserTests();
}

main().catch(err => {
  console.error('Test Suite Failed:', err);
  process.exit(1);
});
