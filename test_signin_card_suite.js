const { chromium } = require('playwright');
const path = require('path');

const artifactDir = 'C:\\Users\\DELL\\.gemini\\antigravity\\brain\\cc9b9613-c2e3-455a-9235-fe78d84a0aea';

function assert(cond, msg) {
  if (!cond) {
    console.error('FAILED ASSERTION:', msg);
    throw new Error('Assertion Failed: ' + msg);
  }
}

async function runTests() {
  console.log('====================================================');
  console.log('RUNNING RAGAA SIGN-IN-CARD-2 TEST SUITE (NEXT.JS)');
  console.log('====================================================');

  let browser;
  try {
    browser = await chromium.launch({ channel: 'msedge', headless: true });
  } catch (e) {
    browser = await chromium.launch({ headless: true });
  }
  const context = await browser.newContext();
  const page = await context.newPage();

  // Test 1: Desktop Viewport (1366x850)
  console.log('\n--- 1. Testing Desktop Viewport (1366x850) ---');
  await page.setViewportSize({ width: 1366, height: 850 });
  await page.goto('http://127.0.0.1:3001/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // Verify Heading & Kannada Subtitle
  const headingText = await page.textContent('h1');
  console.log('Heading text:', headingText);
  assert(headingText && headingText.includes('Welcome back'), 'H1 must contain Welcome back');

  const kannadaSub = await page.locator('text=ಮತ್ತೆ ಸ್ವಾಗತ').count();
  console.log('Kannada subtitle count:', kannadaSub);
  assert(kannadaSub > 0, 'Kannada subtitle ಮತ್ತೆ ಸ್ವಾಗತ must be present');

  // Verify Demo Mode Banner
  const demoBanner = await page.locator('text=Demo mode: any 6-digit code works').count();
  console.log('Demo mode banner present:', demoBanner > 0);
  assert(demoBanner > 0, 'Demo mode banner must be visible');

  const desktopScreenshot = path.join(artifactDir, 'signin_desktop_1366.png');
  await page.screenshot({ path: desktopScreenshot });
  console.log('Captured desktop screenshot:', desktopScreenshot);

  // Test 2: Tablet Viewport (768x1024)
  console.log('\n--- 2. Testing Tablet Viewport (768x1024) ---');
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.waitForTimeout(300);
  const tabletScreenshot = path.join(artifactDir, 'signin_tablet_768.png');
  await page.screenshot({ path: tabletScreenshot });
  console.log('Captured tablet screenshot:', tabletScreenshot);

  // Test 3: Mobile Phone Viewport (360x780)
  console.log('\n--- 3. Testing Mobile Phone Viewport (360x780) ---');
  await page.setViewportSize({ width: 360, height: 780 });
  await page.waitForTimeout(300);
  const phoneScreenshot = path.join(artifactDir, 'signin_phone_360.png');
  await page.screenshot({ path: phoneScreenshot });
  console.log('Captured phone screenshot:', phoneScreenshot);

  // Test 4: Tab Switching (Email <-> Mobile)
  console.log('\n--- 4. Testing Tab Switching ---');
  await page.click('button:has-text("Mobile")');
  await page.waitForTimeout(400);

  const phoneInputVisible = await page.locator('input[type="tel"]').isVisible();
  console.log('Phone input visible on Mobile tab:', phoneInputVisible);
  assert(phoneInputVisible, 'Phone input must be visible on Mobile tab');

  const mobileScreenshot = path.join(artifactDir, 'signin_mobile_tab.png');
  await page.screenshot({ path: mobileScreenshot });
  console.log('Captured mobile tab screenshot:', mobileScreenshot);

  // Switch back to Email tab
  await page.click('button:has-text("Email")');
  await page.waitForTimeout(400);
  const emailInputVisible = await page.locator('input[type="email"]').isVisible();
  assert(emailInputVisible, 'Email input must be visible when returning to Email tab');

  // Test 5: Email Code Submission & SixBoxCodeInput Flow
  console.log('\n--- 5. Testing Email Code Flow ---');
  await page.fill('input[type="email"]', 'listener@ragaa.music');
  await page.click('button[type="submit"]:has-text("Send code")');
  
  // Wait for 6-box input to appear
  const firstBox = page.locator('input[inputmode="numeric"]').first();
  await firstBox.waitFor({ timeout: 6000 });

  // Verify transition to 6-box input
  const sixBoxes = await page.locator('input[inputmode="numeric"]').count();
  console.log('SixBoxCodeInput boxes count:', sixBoxes);
  assert(sixBoxes === 6, 'Six discrete code boxes must be rendered');

  // Verify Verify button is disabled when empty
  const isVerifyDisabled = await page.locator('button:has-text("Verify & Continue")').isDisabled();
  console.log('Verify button initially disabled:', isVerifyDisabled);
  assert(isVerifyDisabled, 'Verify button must be disabled until 6 digits entered');

  // Test error state with "000000" using auto-advance keyboard typing
  console.log('Testing incorrect code simulation (000000) via auto-advance keyboard...');
  await firstBox.focus();
  await page.keyboard.type('000000', { delay: 100 });
  await page.waitForTimeout(400);

  const errorBtn = page.locator('button:has-text("Verify & Continue")');
  await errorBtn.click();
  await page.waitForTimeout(1000);

  const errorMsg = await page.textContent('div[aria-live="assertive"]');
  console.log('Error message received:', errorMsg);
  assert(errorMsg && errorMsg.includes('Incorrect code'), 'Error message must show on wrong code');

  const errorScreenshot = path.join(artifactDir, 'signin_error_shake.png');
  await page.screenshot({ path: errorScreenshot });
  console.log('Captured error state screenshot:', errorScreenshot);

  // Clear code via backspace or click "Edit email" and re-send
  console.log('Clicking "Edit email" to return and re-enter code...');
  await page.click('button:has-text("Edit email")');
  await page.waitForTimeout(400);
  await page.click('button[type="submit"]:has-text("Send code")');
  await firstBox.waitFor({ timeout: 6000 });

  // Test full code paste via clipboard data: "849201"
  console.log('Testing full paste of "849201" on first box...');
  await firstBox.focus();
  await page.evaluate(() => {
    const box = document.querySelector('input[inputmode="numeric"]');
    const dt = new DataTransfer();
    dt.setData('text/plain', '849201');
    const pasteEv = new ClipboardEvent('paste', {
      clipboardData: dt,
      bubbles: true,
      cancelable: true
    });
    box.dispatchEvent(pasteEv);
  });
  // On paste of 6 digits, onComplete automatically triggers verification and transitions to profile setup
  console.log('Waiting for automatic verification and transition to profile setup...');
  const profileStep = page.locator('text=Almost there!');
  await profileStep.waitFor({ timeout: 8000 });

  const profileStepVisible = await profileStep.isVisible();
  console.log('New user onboarding step visible:', profileStepVisible);
  assert(profileStepVisible, 'Profile onboarding step must appear for new user');

  const profileScreenshot = path.join(artifactDir, 'signin_profile_step.png');
  await page.screenshot({ path: profileScreenshot });
  console.log('Captured profile setup screenshot:', profileScreenshot);

  // Complete profile
  await page.fill('#profile-name', 'Vinay Samaldar');
  await page.click('button:has-text("Get Started")');
  await page.waitForTimeout(1000);

  // Verify localStorage session
  const storedSession = await page.evaluate(() => localStorage.getItem('ragaa_user_session'));
  console.log('Stored user session in localStorage:', storedSession);
  assert(storedSession && storedSession.includes('Vinay Samaldar'), 'Session must be saved in localStorage');

  await browser.close();
  console.log('\n====================================================');
  console.log('ALL RAGAA SIGN-IN-CARD-2 TESTS COMPLETED SUCCESSFULLY!');
  console.log('====================================================\n');
}

runTests().catch(err => {
  console.error('Test Suite Failed:', err);
  process.exit(1);
});
