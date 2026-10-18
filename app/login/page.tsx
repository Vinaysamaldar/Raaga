'use client'

import React, { Suspense } from 'react';
import { SignInCard2 } from "@/components/ui/sign-in-card-2";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0B1110] flex items-center justify-center text-white/50 text-sm">Loading Ragaa Login...</div>}>
      <SignInCard2 />
    </Suspense>
  );
}
