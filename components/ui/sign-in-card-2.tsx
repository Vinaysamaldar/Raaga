'use client'

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import { Mail, Phone, ArrowRight, ArrowLeft, Check, Sparkles, AlertCircle } from 'lucide-react';
import { cn } from "@/lib/utils";
import { SixBoxCodeInput } from "./six-box-code-input";
import { useRagaaAuth } from "@/hooks/use-ragaa-auth";

// Pill Styled Input matching Ragaa Design System
function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-11 w-full rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-[var(--ragaa-text,#E3EAE6)] shadow-sm transition-all duration-200 outline-none",
        "placeholder:text-white/40 placeholder:font-normal",
        "focus:bg-white/10 focus:border-[var(--ragaa-saffron,#F2A900)] focus:ring-2 focus:ring-[var(--ragaa-saffron,#F2A900)]/30",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
}

// Country Codes for Mobile Tab
const COUNTRY_CODES = [
  { code: '+91', country: 'IN', label: 'India (+91)' },
  { code: '+1', country: 'US', label: 'United States (+1)' },
  { code: '+44', country: 'GB', label: 'United Kingdom (+44)' },
  { code: '+971', country: 'AE', label: 'UAE (+971)' },
  { code: '+65', country: 'SG', label: 'Singapore (+65)' },
  { code: '+61', country: 'AU', label: 'Australia (+61)' },
  { code: '+49', country: 'DE', label: 'Germany (+49)' },
  { code: '+1', country: 'CA', label: 'Canada (+1)' }
];

export function SignInCard2({ className }: { className?: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get('return') || '/';

  const {
    user,
    isLoading,
    authError,
    isDemoMode,
    requestEmailCode,
    verifyEmailCode,
    requestMobileOtp,
    verifyMobileOtp,
    signInWithGoogle,
    completeProfile,
    setAuthError
  } = useRagaaAuth();

  // Navigation Guard: if already signed in, redirect to returnUrl or home
  useEffect(() => {
    if (user && !user.isNewUser) {
      if (typeof window !== 'undefined' && window.location.pathname.includes('/login')) {
        router.push(returnUrl === '/login' ? '/' : returnUrl);
      }
    }
  }, [user, returnUrl, router]);

  // Auth Card State
  const [activeTab, setActiveTab] = useState<'email' | 'mobile'>('email');
  const [step, setStep] = useState<'input' | 'verify' | 'profile'>('input');
  
  // Input values
  const [email, setEmail] = useState('');
  const [countryCode, setCountryCode] = useState('+91');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [code, setCode] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [focusedInput, setFocusedInput] = useState<string | null>(null);

  // New User Profile Setup State
  const [profileName, setProfileName] = useState('');
  const [profileLang, setProfileLang] = useState<'kn' | 'en' | 'both'>('kn');

  // Timer & Security Lockout State
  const [resendTimer, setResendTimer] = useState(30);
  const [canResend, setCanResend] = useState(false);
  const [showSpamHint, setShowSpamHint] = useState(false);
  const [failedAttempts, setFailedAttempts] = useState(0);
  const [isLocked, setIsLocked] = useState(false);
  const [lockedMinutes, setLockedMinutes] = useState(15);

  // Responsive, Touch & Reduced-Motion Detection
  const [isMobileOrTouch, setIsMobileOrTouch] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [isTabHidden, setIsTabHidden] = useState(false);

  useEffect(() => {
    const checkMotionAndDevice = () => {
      const isTouch = window.matchMedia('(pointer: coarse)').matches;
      const isNarrow = window.innerWidth < 768;
      setIsMobileOrTouch(isTouch || isNarrow);

      const rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      setPrefersReducedMotion(rm);
    };

    checkMotionAndDevice();
    window.addEventListener('resize', checkMotionAndDevice);

    const handleVisibility = () => {
      setIsTabHidden(document.hidden);
    };
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      window.removeEventListener('resize', checkMotionAndDevice);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  // 3D Motion Values
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const rotateX = useTransform(mouseY, [-300, 300], isMobileOrTouch || prefersReducedMotion ? [0, 0] : [8, -8]);
  const rotateY = useTransform(mouseX, [-300, 300], isMobileOrTouch || prefersReducedMotion ? [0, 0] : [-8, 8]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isMobileOrTouch || prefersReducedMotion) return;
    const rect = e.currentTarget.getBoundingClientRect();
    mouseX.set(e.clientX - rect.left - rect.width / 2);
    mouseY.set(e.clientY - rect.top - rect.height / 2);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  // Keyboard Navigation: Escape goes back
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && step === 'verify') {
        setStep('input');
        setCode('');
        setAuthError(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [step, setAuthError]);

  // Resend countdown timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (step === 'verify' && resendTimer > 0) {
      interval = setInterval(() => {
        setResendTimer(prev => {
          if (prev <= 1) {
            setCanResend(true);
            setShowSpamHint(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [step, resendTimer]);

  // WebOTP API for Mobile Tab
  useEffect(() => {
    if (activeTab === 'mobile' && step === 'verify' && 'OTPCredential' in window) {
      const ac = new AbortController();
      (navigator as any).credentials.get({
        otp: { transport: ['sms'] },
        signal: ac.signal
      }).then((otp: any) => {
        if (otp && otp.code && otp.code.length === 6) {
          setCode(otp.code);
          handleVerify(otp.code);
        }
      }).catch(() => {});

      return () => ac.abort();
    }
  }, [activeTab, step]);

  // Actions
  const handleSendCode = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAuthError(null);

    if (activeTab === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email.trim() || !emailRegex.test(email.trim())) {
        setAuthError('Please enter a valid email address (e.g. name@example.com)');
        return;
      }
      const ok = await requestEmailCode(email.trim());
      if (ok) {
        setStep('verify');
        setResendTimer(30);
        setCanResend(false);
        setShowSpamHint(false);
        setCode('');
      }
    } else {
      const phoneDigits = phoneNumber.replace(/[^0-9]/g, '');
      if (phoneDigits.length < 8) {
        setAuthError('Please enter a valid phone number (at least 8 digits)');
        return;
      }
      const fullPhone = `${countryCode} ${phoneDigits}`;
      const ok = await requestMobileOtp(fullPhone);
      if (ok) {
        setStep('verify');
        setResendTimer(30);
        setCanResend(false);
        setShowSpamHint(false);
        setCode('');
      }
    }
  };

  const handleVerify = async (codeToVerify?: string) => {
    const finalCode = codeToVerify || code;
    if (finalCode.length !== 6) return;
    if (isLocked) return;

    setAuthError(null);

    if (activeTab === 'email') {
      const result = await verifyEmailCode(email, finalCode, rememberMe);
      if (result.success) {
        setFailedAttempts(0);
        if (result.isNewUser) {
          setProfileName(email.split('@')[0]);
          setStep('profile');
        } else {
          router.push(returnUrl === '/login' ? '/' : returnUrl);
        }
      } else {
        const attempts = failedAttempts + 1;
        setFailedAttempts(attempts);
        if (attempts >= 5) {
          setIsLocked(true);
          setLockedMinutes(15);
          setAuthError('Too many failed attempts. Locked for 15 minutes.');
        } else {
          setAuthError(result.error || `Incorrect code. ${5 - attempts} attempts left.`);
        }
      }
    } else {
      const fullPhone = `${countryCode} ${phoneNumber}`;
      const result = await verifyMobileOtp(fullPhone, finalCode, rememberMe);
      if (result.success) {
        setFailedAttempts(0);
        if (result.isNewUser) {
          setProfileName('Kannada Listener');
          setStep('profile');
        } else {
          router.push(returnUrl === '/login' ? '/' : returnUrl);
        }
      } else {
        const attempts = failedAttempts + 1;
        setFailedAttempts(attempts);
        if (attempts >= 5) {
          setIsLocked(true);
          setLockedMinutes(15);
          setAuthError('Too many failed attempts. Locked for 15 minutes.');
        } else {
          setAuthError(result.error || `Incorrect OTP. ${5 - attempts} attempts left.`);
        }
      }
    }
  };

  const handleGoogleSignIn = async () => {
    setAuthError(null);
    const ok = await signInWithGoogle(rememberMe);
    if (ok) {
      router.push(returnUrl === '/login' ? '/' : returnUrl);
    }
  };

  const handleContinueAsGuest = () => {
    try {
      localStorage.removeItem('ragaa_user_session');
    } catch(e) {}
    router.push(returnUrl === '/login' ? '/' : returnUrl);
  };

  const handleCompleteProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profileName.trim()) {
      setAuthError('Please enter your name to finish setup');
      return;
    }
    await completeProfile({
      displayName: profileName.trim(),
      language: profileLang
    });
    router.push(returnUrl === '/login' ? '/' : returnUrl);
  };

  return (
    <div className={cn(
      "min-h-screen w-full relative overflow-hidden flex items-center justify-center p-4 sm:p-6",
      className
    )}>
      {/* Background Layer: Gradient from #0B1110 through #101A17 to Black */}
      <div 
        className="absolute inset-0 -z-30 bg-gradient-to-b from-[#0B1110] via-[#101A17] to-black"
        style={{
          background: 'linear-gradient(180deg, #0B1110 0%, #101A17 55%, #000000 100%)'
        }}
      />
      
      {/* Subtle Noise Texture Overlay */}
      <div 
        className="absolute inset-0 -z-20 opacity-[0.035] mix-blend-soft-light pointer-events-none" 
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundSize: '200px 200px'
        }}
      />

      {/* Top Radial Glow (Saffron #F2A900 default, variable-driven) */}
      <div 
        className="absolute top-0 left-1/2 transform -translate-x-1/2 w-[120vw] max-w-[900px] h-[50vh] rounded-b-[50%] blur-[90px] -z-10 pointer-events-none opacity-20"
        style={{
          background: `radial-gradient(ellipse at top, rgba(var(--glow-rgb, 242 169 0), 0.35), transparent 70%)`
        }}
      />

      {/* Slow Pulsing Top Glow (Motion respected) */}
      {!prefersReducedMotion && !isTabHidden && (
        <motion.div 
          className="absolute top-0 left-1/2 transform -translate-x-1/2 w-[100vw] max-w-[800px] h-[45vh] rounded-b-full blur-[70px] -z-10 pointer-events-none"
          style={{
            background: `radial-gradient(ellipse at top, rgba(var(--glow-rgb, 242 169 0), 0.25), transparent 65%)`
          }}
          animate={{ 
            opacity: [0.15, 0.28, 0.15],
            scale: [0.98, 1.02, 0.98]
          }}
          transition={{ 
            duration: 8, 
            repeat: Infinity,
            repeatType: "mirror"
          }}
        />
      )}

      {/* Slow Pulsing Bottom Glow */}
      {!prefersReducedMotion && !isTabHidden && (
        <motion.div 
          className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-[90vw] max-w-[700px] h-[40vh] rounded-t-full blur-[80px] -z-10 pointer-events-none"
          style={{
            background: `radial-gradient(ellipse at bottom, rgba(var(--glow-rgb, 242 169 0), 0.2), transparent 70%)`
          }}
          animate={{ 
            opacity: [0.12, 0.24, 0.12],
            scale: [1, 1.08, 1]
          }}
          transition={{ 
            duration: 7, 
            repeat: Infinity,
            repeatType: "mirror",
            delay: 1
          }}
        />
      )}

      {/* Animated Subtle Corner Glow Spots */}
      {!isMobileOrTouch && !prefersReducedMotion && (
        <>
          <div className="absolute left-1/4 top-1/4 w-80 h-80 rounded-full blur-[100px] pointer-events-none animate-pulse opacity-15"
            style={{ background: 'rgba(var(--glow-rgb, 242 169 0), 0.15)' }}
          />
          <div className="absolute right-1/4 bottom-1/4 w-80 h-80 rounded-full blur-[100px] pointer-events-none animate-pulse delay-1000 opacity-15"
            style={{ background: 'rgba(var(--glow-rgb, 242 169 0), 0.15)' }}
          />
        </>
      )}

      {/* Main 3D Perspective Wrapper */}
      <motion.div
        initial={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-sm md:max-w-md relative z-10"
        style={{ perspective: isMobileOrTouch ? undefined : 1400 }}
      >
        <motion.div
          className="relative"
          style={isMobileOrTouch || prefersReducedMotion ? undefined : { rotateX, rotateY }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          whileHover={isMobileOrTouch || prefersReducedMotion ? undefined : { z: 6 }}
        >
          <div className="relative group">
            {/* Edge Glow Hover Effect */}
            {!prefersReducedMotion && (
              <motion.div 
                className="absolute -inset-[1px] rounded-2xl opacity-0 group-hover:opacity-70 transition-opacity duration-700 pointer-events-none"
                animate={{
                  boxShadow: [
                    "0 0 12px 2px rgba(var(--glow-rgb, 242 169 0), 0.08)",
                    "0 0 20px 5px rgba(var(--glow-rgb, 242 169 0), 0.16)",
                    "0 0 12px 2px rgba(var(--glow-rgb, 242 169 0), 0.08)"
                  ],
                  opacity: [0.3, 0.6, 0.3]
                }}
                transition={{ 
                  duration: 4, 
                  repeat: Infinity, 
                  ease: "easeInOut", 
                  repeatType: "mirror" 
                }}
              />
            )}

            {/* Traveling Light Beams (Top beam has saffron tint) */}
            {!prefersReducedMotion && !isTabHidden && (
              <div className="absolute -inset-[1px] rounded-2xl overflow-hidden pointer-events-none">
                {/* Top light beam - Saffron Tinted */}
                <motion.div 
                  className="absolute top-0 left-0 h-[2.5px] w-[50%] opacity-80"
                  style={{
                    background: 'linear-gradient(90deg, transparent, rgba(var(--glow-rgb, 242 169 0), 0.9) 40%, #FFFFFF 60%, transparent)'
                  }}
                  animate={{ 
                    left: ["-50%", "100%"],
                    opacity: [0.3, 0.8, 0.3]
                  }}
                  transition={{ 
                    left: { duration: 2.8, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.8 },
                    opacity: { duration: 1.4, repeat: Infinity, repeatType: "mirror" }
                  }}
                />
                
                {/* Right light beam */}
                <motion.div 
                  className="absolute top-0 right-0 h-[50%] w-[2.5px] bg-gradient-to-b from-transparent via-white/80 to-transparent opacity-70"
                  animate={{ 
                    top: ["-50%", "100%"],
                    opacity: [0.3, 0.7, 0.3]
                  }}
                  transition={{ 
                    top: { duration: 2.8, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.8, delay: 0.7 },
                    opacity: { duration: 1.4, repeat: Infinity, repeatType: "mirror", delay: 0.7 }
                  }}
                />
                
                {/* Bottom light beam */}
                <motion.div 
                  className="absolute bottom-0 right-0 h-[2.5px] w-[50%] bg-gradient-to-r from-transparent via-white/80 to-transparent opacity-70"
                  animate={{ 
                    right: ["-50%", "100%"],
                    opacity: [0.3, 0.7, 0.3]
                  }}
                  transition={{ 
                    right: { duration: 2.8, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.8, delay: 1.4 },
                    opacity: { duration: 1.4, repeat: Infinity, repeatType: "mirror", delay: 1.4 }
                  }}
                />
                
                {/* Left light beam */}
                <motion.div 
                  className="absolute bottom-0 left-0 h-[50%] w-[2.5px] bg-gradient-to-b from-transparent via-white/80 to-transparent opacity-70"
                  animate={{ 
                    bottom: ["-50%", "100%"],
                    opacity: [0.3, 0.7, 0.3]
                  }}
                  transition={{ 
                    bottom: { duration: 2.8, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.8, delay: 2.1 },
                    opacity: { duration: 1.4, repeat: Infinity, repeatType: "mirror", delay: 2.1 }
                  }}
                />

                {/* Corner Glow Spots */}
                <div className="absolute top-0 left-0 h-1.5 w-1.5 rounded-full bg-[var(--ragaa-saffron,#F2A900)]/80 blur-[1px]" />
                <div className="absolute top-0 right-0 h-1.5 w-1.5 rounded-full bg-white/70 blur-[1px]" />
                <div className="absolute bottom-0 right-0 h-1.5 w-1.5 rounded-full bg-white/70 blur-[1px]" />
                <div className="absolute bottom-0 left-0 h-1.5 w-1.5 rounded-full bg-white/70 blur-[1px]" />
              </div>
            )}

            {/* The Glass Card Body */}
            <div className="relative bg-black/40 backdrop-blur-xl rounded-2xl p-5 sm:p-7 border border-white/[0.06] shadow-2xl overflow-hidden">
              {/* Card Inner Subtle Diagonal Patterns */}
              <div 
                className="absolute inset-0 opacity-[0.03] pointer-events-none" 
                style={{
                  backgroundImage: `linear-gradient(135deg, white 0.5px, transparent 0.5px), linear-gradient(45deg, white 0.5px, transparent 0.5px)`,
                  backgroundSize: '28px 28px'
                }}
              />

              {/* Demo Mode Fallback Banner */}
              {isDemoMode && (
                <div className="mb-4 px-3 py-1.5 rounded-full bg-[var(--ragaa-saffron,#F2A900)]/10 border border-[var(--ragaa-saffron,#F2A900)]/30 flex items-center justify-center gap-1.5 text-xs text-[var(--ragaa-saffron,#F2A900)] font-medium">
                  <Sparkles className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>Demo mode: any 6-digit code works (e.g. 849201)</span>
                </div>
              )}

              {/* Logo & Header Section */}
              <div className="text-center space-y-1 mb-5">
                <motion.div
                  initial={prefersReducedMotion ? { opacity: 0 } : { scale: 0.6, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring", duration: 0.7 }}
                  className="mx-auto w-12 h-12 rounded-2xl border border-[var(--ragaa-saffron,#F2A900)]/40 p-0.5 flex items-center justify-center relative overflow-hidden shadow-lg shadow-[var(--ragaa-saffron,#F2A900)]/20 bg-black/60 flex-shrink-0"
                  style={{ width: '48px', height: '48px', minWidth: '48px', minHeight: '48px' }}
                >
                  <img 
                    src="/ragaa_logo.jpg" 
                    alt="Ragaa Logo" 
                    className="w-full h-full object-cover rounded-xl"
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                </motion.div>

                <h1 className="text-xl sm:text-2xl font-black text-[var(--ragaa-text,#E3EAE6)] tracking-tight pt-1">
                  Welcome back
                </h1>
                
                <p className="text-xs sm:text-sm font-semibold text-[var(--ragaa-saffron,#F2A900)]">
                  ಮತ್ತೆ ಸ್ವಾಗತ
                </p>

                <p className="text-white/50 text-xs pt-0.5">
                  Sign in to continue to Ragaa
                </p>
              </div>

              {/* Step 1 & 2: Pill Segmented Tabs (Email | Mobile) */}
              {step !== 'profile' && (
                <div className="flex p-1 rounded-full bg-white/5 border border-white/10 mb-5 relative">
                  <button
                    type="button"
                    onClick={() => { setActiveTab('email'); setStep('input'); setAuthError(null); }}
                    className={cn(
                      "flex-1 py-1.5 text-xs font-semibold rounded-full transition-all duration-200 relative z-10 text-center",
                      activeTab === 'email' ? "text-black" : "text-white/60 hover:text-white"
                    )}
                  >
                    {activeTab === 'email' && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute inset-0 rounded-full bg-[var(--ragaa-mint-white,#DDE6E1)] -z-10 shadow-sm"
                        transition={{ type: "spring", stiffness: 450, damping: 30 }}
                      />
                    )}
                    Email
                  </button>

                  <button
                    type="button"
                    onClick={() => { setActiveTab('mobile'); setStep('input'); setAuthError(null); }}
                    className={cn(
                      "flex-1 py-1.5 text-xs font-semibold rounded-full transition-all duration-200 relative z-10 text-center",
                      activeTab === 'mobile' ? "text-black" : "text-white/60 hover:text-white"
                    )}
                  >
                    {activeTab === 'mobile' && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute inset-0 rounded-full bg-[var(--ragaa-mint-white,#DDE6E1)] -z-10 shadow-sm"
                        transition={{ type: "spring", stiffness: 450, damping: 30 }}
                      />
                    )}
                    Mobile
                  </button>
                </div>
              )}

              {/* Form Content Slider via AnimatePresence */}
              <AnimatePresence mode="wait">
                {/* ================= STEP 1: INPUT SCREEN ================= */}
                {step === 'input' && (
                  <motion.form
                    key="step-input"
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 16 }}
                    transition={{ duration: 0.25 }}
                    onSubmit={handleSendCode}
                    className="space-y-4"
                  >
                    {activeTab === 'email' ? (
                      /* Email Input */
                      <div className="space-y-1.5">
                        <label htmlFor="email-input" className="text-xs font-medium text-white/70 block pl-1">
                          Email address
                        </label>
                        <div className="relative flex items-center">
                          <Mail className={cn(
                            "absolute left-4 w-4 h-4 transition-colors duration-200 pointer-events-none",
                            focusedInput === "email" ? "text-[var(--ragaa-saffron,#F2A900)]" : "text-white/50"
                          )} />
                          <Input
                            id="email-input"
                            type="email"
                            required
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            onFocus={() => setFocusedInput("email")}
                            onBlur={() => setFocusedInput(null)}
                            className="pl-11 pr-4"
                          />
                        </div>
                      </div>
                    ) : (
                      /* Mobile Phone Input */
                      <div className="space-y-1.5">
                        <label htmlFor="phone-input" className="text-xs font-medium text-white/70 block pl-1">
                          Mobile number
                        </label>
                        <div className="flex gap-2">
                          {/* Country Code Select */}
                          <div className="relative">
                            <select
                              value={countryCode}
                              onChange={(e) => setCountryCode(e.target.value)}
                              aria-label="Select Country Code"
                              className="h-11 rounded-full border border-white/10 bg-white/5 px-3 text-xs text-white appearance-none pr-7 outline-none focus:border-[var(--ragaa-saffron,#F2A900)] focus:ring-2 focus:ring-[var(--ragaa-saffron,#F2A900)]/30 cursor-pointer"
                            >
                              {COUNTRY_CODES.map((c) => (
                                <option key={c.code + c.country} value={c.code} className="bg-[#101A17] text-white">
                                  {c.code} {c.country}
                                </option>
                              ))}
                            </select>
                            <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-white/40 pointer-events-none text-[10px]">▼</span>
                          </div>

                          {/* Phone input */}
                          <div className="relative flex-1 flex items-center">
                            <Phone className={cn(
                              "absolute left-4 w-4 h-4 transition-colors duration-200 pointer-events-none",
                              focusedInput === "phone" ? "text-[var(--ragaa-saffron,#F2A900)]" : "text-white/50"
                            )} />
                            <Input
                              id="phone-input"
                              type="tel"
                              required
                              placeholder="98765 43210"
                              value={phoneNumber}
                              onChange={(e) => setPhoneNumber(e.target.value)}
                              onFocus={() => setFocusedInput("phone")}
                              onBlur={() => setFocusedInput(null)}
                              className="pl-11 pr-4"
                            />
                          </div>
                        </div>
                        <p className="text-[11px] text-white/40 pl-1">Standard SMS rates may apply.</p>
                      </div>
                    )}

                    {/* Remember me Checkbox */}
                    <div className="flex items-center space-x-2.5 pt-1 pl-1">
                      <div className="relative flex items-center">
                        <input
                          id="remember-me"
                          name="remember-me"
                          type="checkbox"
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          className="h-4 w-4 rounded-md border border-white/20 bg-white/5 checked:bg-[var(--ragaa-saffron,#F2A900)] checked:border-[var(--ragaa-saffron,#F2A900)] focus:outline-none focus:ring-2 focus:ring-[var(--ragaa-saffron,#F2A900)]/40 cursor-pointer transition-all duration-150"
                        />
                      </div>
                      <label htmlFor="remember-me" className="text-xs text-white/70 hover:text-white cursor-pointer select-none">
                        Remember me on this device
                      </label>
                    </div>

                    {/* Auth Error Banner with aria-live */}
                    {authError && (
                      <div aria-live="assertive" className="flex items-center gap-2 p-2.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-300">
                        <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
                        <span>{authError}</span>
                      </div>
                    )}

                    {/* Send Code Animated Primary Button */}
                    <motion.button
                      whileHover={isMobileOrTouch || prefersReducedMotion ? undefined : { scale: 1.015 }}
                      whileTap={{ scale: 0.985 }}
                      type="submit"
                      disabled={isLoading}
                      className="w-full relative group/button mt-4"
                    >
                      {/* Button Glow on Hover */}
                      <div className="absolute inset-0 bg-[var(--ragaa-mint-white,#DDE6E1)]/20 rounded-full blur-md opacity-0 group-hover/button:opacity-80 transition-opacity duration-300" />
                      
                      <div className="relative overflow-hidden bg-[var(--ragaa-mint-white,#DDE6E1)] text-[#0B1110] font-semibold h-11 rounded-full transition-all duration-300 flex items-center justify-center shadow-md">
                        {/* Shimmer animation */}
                        {!prefersReducedMotion && (
                          <motion.div 
                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent -z-10"
                            animate={{ x: ['-100%', '100%'] }}
                            transition={{ duration: 1.6, ease: "easeInOut", repeat: Infinity, repeatDelay: 1 }}
                          />
                        )}
                        
                        {isLoading ? (
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-4 h-4 border-2 border-[#0B1110] border-t-transparent rounded-full animate-spin" />
                            <span className="text-xs font-semibold">Sending code...</span>
                          </div>
                        ) : (
                          <span className="flex items-center justify-center gap-1.5 text-sm font-bold">
                            {activeTab === 'email' ? 'Send code' : 'Send OTP'}
                            <ArrowRight className="w-4 h-4 group-hover/button:translate-x-1 transition-transform duration-200" />
                          </span>
                        )}
                      </div>
                    </motion.button>
                  </motion.form>
                )}

                {/* ================= STEP 2: VERIFY SIX-BOX CODE ================= */}
                {step === 'verify' && (
                  <motion.div
                    key="step-verify"
                    initial={{ opacity: 0, x: 16 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -16 }}
                    transition={{ duration: 0.25 }}
                    className="space-y-4"
                  >
                    <div className="flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() => { setStep('input'); setCode(''); setAuthError(null); }}
                        className="flex items-center gap-1 text-xs text-white/60 hover:text-[var(--ragaa-saffron,#F2A900)] transition-colors py-1"
                      >
                        <ArrowLeft className="w-3.5 h-3.5" />
                        <span>Edit {activeTab === 'email' ? 'email' : 'number'}</span>
                      </button>

                      <span className="text-[11px] text-white/40 font-mono">
                        Expires in 10:00
                      </span>
                    </div>

                    <div className="text-center space-y-1">
                      <h3 className="text-sm font-semibold text-white">
                        Enter 6-digit verification code
                      </h3>
                      <p className="text-xs text-white/60">
                        We sent a code to{' '}
                        <strong className="text-[var(--ragaa-mint-white,#DDE6E1)]">
                          {activeTab === 'email' ? email : `${countryCode} ${phoneNumber}`}
                        </strong>
                      </p>
                    </div>

                    {/* Reusable Glass SixBoxCodeInput */}
                    <SixBoxCodeInput
                      value={code}
                      onChange={(newVal) => { setCode(newVal); setAuthError(null); }}
                      onComplete={(completeCode) => handleVerify(completeCode)}
                      disabled={isLoading}
                      error={authError}
                      isLocked={isLocked}
                      lockedMinutesLeft={lockedMinutes}
                    />

                    {/* Resend Timer & Spam Hint */}
                    <div className="flex flex-col items-center justify-center gap-1 text-xs pt-1">
                      {canResend ? (
                        <button
                          type="button"
                          onClick={() => handleSendCode()}
                          disabled={isLoading || isLocked}
                          className="text-[var(--ragaa-saffron,#F2A900)] hover:underline font-semibold"
                        >
                          Resend verification code
                        </button>
                      ) : (
                        <span className="text-white/40 font-mono">
                          Resend code in 00:{resendTimer < 10 ? `0${resendTimer}` : resendTimer}
                        </span>
                      )}

                      {showSpamHint && (
                        <p className="text-[11px] text-white/40 animate-fade-in">
                          Can't find it? Check your spam/junk folder.
                        </p>
                      )}
                    </div>

                    {/* Verify Action Button */}
                    <motion.button
                      whileHover={isMobileOrTouch || prefersReducedMotion || code.length !== 6 ? undefined : { scale: 1.015 }}
                      whileTap={{ scale: 0.985 }}
                      type="button"
                      disabled={isLoading || code.length !== 6 || isLocked}
                      onClick={() => handleVerify()}
                      className={cn(
                        "w-full relative group/button mt-3",
                        (code.length !== 6 || isLocked) && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      <div className="relative overflow-hidden bg-[var(--ragaa-saffron,#F2A900)] text-[#0B1110] font-bold h-11 rounded-full transition-all duration-300 flex items-center justify-center shadow-lg shadow-[var(--ragaa-saffron,#F2A900)]/20">
                        {isLoading ? (
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-4 h-4 border-2 border-[#0B1110] border-t-transparent rounded-full animate-spin" />
                            <span className="text-xs font-semibold">Verifying code...</span>
                          </div>
                        ) : (
                          <span className="flex items-center justify-center gap-1.5 text-sm font-bold">
                            Verify & Continue
                            <Check className="w-4 h-4" />
                          </span>
                        )}
                      </div>
                    </motion.button>
                  </motion.div>
                )}

                {/* ================= STEP 3: NEW USER ONBOARDING ================= */}
                {step === 'profile' && (
                  <motion.form
                    key="step-profile"
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    onSubmit={handleCompleteProfile}
                    className="space-y-4"
                  >
                    <div className="text-center space-y-1">
                      <h3 className="text-base font-bold text-white">Almost there! • ಸ್ವಲ್ಪವೇ ಬಾಕಿ ಇದೆ</h3>
                      <p className="text-xs text-white/60">Customize your Kannada listening experience</p>
                    </div>

                    {/* Name input */}
                    <div className="space-y-1.5">
                      <label htmlFor="profile-name" className="text-xs font-medium text-white/70 block pl-1">
                        Your Name
                      </label>
                      <Input
                        id="profile-name"
                        type="text"
                        required
                        placeholder="e.g. Vinay Samaldar"
                        value={profileName}
                        onChange={(e) => setProfileName(e.target.value)}
                        className="px-4"
                      />
                    </div>

                    {/* Language Preference */}
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-white/70 block pl-1">
                        Preferred Language
                      </label>
                      <div className="grid grid-cols-3 gap-2">
                        {[
                          { id: 'kn', label: 'ಕನ್ನಡ' },
                          { id: 'en', label: 'English' },
                          { id: 'both', label: 'Both / ಎರಡೂ' }
                        ].map((lang) => (
                          <button
                            key={lang.id}
                            type="button"
                            onClick={() => setProfileLang(lang.id as any)}
                            className={cn(
                              "py-2 rounded-xl text-xs font-semibold border transition-all duration-200",
                              profileLang === lang.id
                                ? "bg-[var(--ragaa-saffron,#F2A900)] text-black border-[var(--ragaa-saffron,#F2A900)]"
                                : "bg-white/5 border-white/10 text-white/70 hover:border-white/30"
                            )}
                          >
                            {lang.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Get Started Button */}
                    <motion.button
                      whileHover={isMobileOrTouch || prefersReducedMotion ? undefined : { scale: 1.015 }}
                      whileTap={{ scale: 0.985 }}
                      type="submit"
                      disabled={isLoading}
                      className="w-full relative mt-3"
                    >
                      <div className="relative overflow-hidden bg-[var(--ragaa-mint-white,#DDE6E1)] text-[#0B1110] font-bold h-11 rounded-full flex items-center justify-center">
                        <span className="flex items-center justify-center gap-1.5 text-sm font-bold">
                          Get Started • ಪ್ರಾರಂಭಿಸಿ
                          <ArrowRight className="w-4 h-4" />
                        </span>
                      </div>
                    </motion.button>
                  </motion.form>
                )}
              </AnimatePresence>

              {/* Minimal Divider */}
              <div className="relative my-4 flex items-center">
                <div className="flex-grow border-t border-white/10"></div>
                <span className="mx-3 text-[11px] text-white/40 uppercase tracking-widest font-mono">
                  or
                </span>
                <div className="flex-grow border-t border-white/10"></div>
              </div>

              {/* Google Sign In with Multi-color SVG */}
              <motion.button
                whileHover={isMobileOrTouch || prefersReducedMotion ? undefined : { scale: 1.015 }}
                whileTap={{ scale: 0.985 }}
                type="button"
                onClick={handleGoogleSignIn}
                disabled={isLoading}
                className="w-full relative group/google"
              >
                <div className="absolute inset-0 bg-white/5 rounded-full blur opacity-0 group-hover/google:opacity-70 transition-opacity duration-300" />
                
                <div className="relative overflow-hidden bg-white/5 text-white font-medium h-11 rounded-full border border-white/10 hover:border-white/20 transition-all duration-300 flex items-center justify-center gap-2.5">
                  {/* Real Multi-color Google SVG */}
                  <svg width="18" height="18" viewBox="0 0 24 24" className="w-4 h-4 flex-shrink-0">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                  </svg>
                  
                  <span className="text-white/80 group-hover/google:text-white transition-colors text-xs font-semibold">
                    Sign in with Google
                  </span>
                </div>
              </motion.button>

              {/* Continue as Guest Button */}
              <div className="text-center mt-2.5">
                <button
                  type="button"
                  onClick={handleContinueAsGuest}
                  className="text-xs text-[var(--ragaa-saffron,#F2A900)] hover:underline font-semibold py-1 px-3"
                >
                  Continue as guest (Browse & play)
                </button>
              </div>

              {/* Microcopy & Legal Links */}
              <div className="text-center space-y-1.5 mt-4 pt-2 border-t border-white/[0.06]">
                <p className="text-[11px] text-white/50 leading-relaxed">
                  New here? Just enter your email or number, we will create your account.
                </p>

                <p className="text-[10px] text-white/40">
                  By continuing, you agree to Ragaa's{' '}
                  <Link href="/terms" className="underline hover:text-white/70">
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link href="/privacy" className="underline hover:text-white/70">
                    Privacy Policy
                  </Link>.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

export const Component = SignInCard2;
export default SignInCard2;
