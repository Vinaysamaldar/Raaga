import React, { Suspense } from 'react';
import { DemoOne } from "@/components/ui/demo";

export default function DemoPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0B1110]" />}>
      <DemoOne />
    </Suspense>
  );
}
