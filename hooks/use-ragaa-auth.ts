'use client'

import { useState, useEffect, useCallback } from 'react';

export interface RagaaUser {
  uid: string;
  email?: string;
  phone?: string;
  displayName?: string;
  photoURL?: string;
  language?: 'kn' | 'en' | 'both';
  provider: 'email' | 'phone' | 'google';
  isNewUser?: boolean;
}

export function useRagaaAuth() {
  const [user, setUser] = useState<RagaaUser | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  // Check environment & existing session
  useEffect(() => {
    setIsMounted(true);
    const hasFirebase = !!(
      process.env.NEXT_PUBLIC_FIREBASE_API_KEY && 
      process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
    );
    setIsDemoMode(!hasFirebase);

    try {
      const stored = localStorage.getItem('ragaa_user_session');
      if (stored) {
        setUser(JSON.parse(stored));
      }
    } catch (e) {
      console.warn('[Ragaa Auth] Error reading session', e);
    }
  }, []);

  const saveUserSession = useCallback((newUser: RagaaUser, remember: boolean = true) => {
    setUser(newUser);
    if (remember) {
      try {
        localStorage.setItem('ragaa_user_session', JSON.stringify(newUser));
      } catch (e) {}
    }
  }, []);

  // Request Email Code
  const requestEmailCode = async (email: string): Promise<boolean> => {
    setIsLoading(true);
    setAuthError(null);

    try {
      if (isDemoMode) {
        // Demo mode simulation with artificial latency
        await new Promise(r => setTimeout(r, 650));
        setIsLoading(false);
        return true;
      }

      // Real Firebase Cloud Function call
      const res = await fetch('/api/request-email-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to send verification code');
      setIsLoading(false);
      return true;
    } catch (err: any) {
      setAuthError(err.message || 'Error sending code. Please try again.');
      setIsLoading(false);
      return false;
    }
  };

  // Verify Email Code
  const verifyEmailCode = async (
    email: string, 
    code: string,
    remember: boolean = true
  ): Promise<{ success: boolean; isNewUser: boolean; error?: string }> => {
    setIsLoading(true);
    setAuthError(null);

    try {
      if (isDemoMode) {
        await new Promise(r => setTimeout(r, 600));

        // Let code "000000" simulate an incorrect code for error testing
        if (code === '000000') {
          setIsLoading(false);
          return { success: false, isNewUser: false, error: 'Incorrect code. 2 attempts left.' };
        }

        const newUser: RagaaUser = {
          uid: 'uid_' + Math.random().toString(36).slice(2, 9),
          email,
          displayName: email.split('@')[0],
          provider: 'email',
          isNewUser: true
        };

        saveUserSession(newUser, remember);
        setIsLoading(false);
        return { success: true, isNewUser: true };
      }

      const res = await fetch('/api/verify-email-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Invalid or expired code');

      const verifiedUser: RagaaUser = {
        uid: data.uid || ('uid_' + Math.random().toString(36).slice(2, 9)),
        email,
        displayName: data.displayName || email.split('@')[0],
        provider: 'email',
        isNewUser: !!data.isNewUser
      };

      saveUserSession(verifiedUser, remember);
      setIsLoading(false);
      return { success: true, isNewUser: verifiedUser.isNewUser || false };
    } catch (err: any) {
      const msg = err.message || 'Verification failed';
      setAuthError(msg);
      setIsLoading(false);
      return { success: false, isNewUser: false, error: msg };
    }
  };

  // Request Mobile OTP
  const requestMobileOtp = async (phoneNumber: string): Promise<boolean> => {
    setIsLoading(true);
    setAuthError(null);

    try {
      await new Promise(r => setTimeout(r, 650));
      setIsLoading(false);
      return true;
    } catch (err: any) {
      setAuthError(err.message || 'Error sending OTP');
      setIsLoading(false);
      return false;
    }
  };

  // Verify Mobile OTP
  const verifyMobileOtp = async (
    phone: string,
    code: string,
    remember: boolean = true
  ): Promise<{ success: boolean; isNewUser: boolean; error?: string }> => {
    setIsLoading(true);
    setAuthError(null);

    try {
      await new Promise(r => setTimeout(r, 600));

      if (code === '000000') {
        setIsLoading(false);
        return { success: false, isNewUser: false, error: 'Incorrect code. 2 attempts left.' };
      }

      const verifiedUser: RagaaUser = {
        uid: 'uid_mob_' + Math.random().toString(36).slice(2, 9),
        phone,
        displayName: 'Kannada Listener',
        provider: 'phone',
        isNewUser: true
      };

      saveUserSession(verifiedUser, remember);
      setIsLoading(false);
      return { success: true, isNewUser: true };
    } catch (err: any) {
      const msg = err.message || 'OTP verification failed';
      setAuthError(msg);
      setIsLoading(false);
      return { success: false, isNewUser: false, error: msg };
    }
  };

  // Google Sign-In
  const signInWithGoogle = async (
    remember: boolean = true
  ): Promise<boolean> => {
    setIsLoading(true);
    setAuthError(null);

    try {
      await new Promise(r => setTimeout(r, 800));

      const googleUser: RagaaUser = {
        uid: 'uid_goog_' + Math.random().toString(36).slice(2, 9),
        email: 'listener@gmail.com',
        displayName: 'Vinay Samaldar',
        photoURL: '',
        provider: 'google',
        isNewUser: false
      };

      saveUserSession(googleUser, remember);
      setIsLoading(false);
      return true;
    } catch (err: any) {
      setAuthError('Google Sign-in was cancelled or encountered an error.');
      setIsLoading(false);
      return false;
    }
  };

  // Update Profile (Onboarding Step)
  const completeProfile = async (data: {
    displayName: string;
    language: 'kn' | 'en' | 'both';
  }): Promise<boolean> => {
    if (!user) return false;
    const updated: RagaaUser = {
      ...user,
      displayName: data.displayName,
      language: data.language,
      isNewUser: false
    };
    saveUserSession(updated, true);
    return true;
  };

  // Sign out
  const signOut = () => {
    setUser(null);
    try {
      localStorage.removeItem('ragaa_user_session');
    } catch (e) {}
  };

  return {
    user,
    isLoading,
    authError,
    isDemoMode,
    isMounted,
    requestEmailCode,
    verifyEmailCode,
    requestMobileOtp,
    verifyMobileOtp,
    signInWithGoogle,
    completeProfile,
    signOut,
    setAuthError
  };
}

export default useRagaaAuth;
