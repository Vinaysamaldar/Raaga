'use client'

import React, { useRef, useEffect } from 'react';
import { cn } from "@/lib/utils";

export interface SixBoxCodeInputProps {
  value: string;
  onChange: (value: string) => void;
  onComplete?: (code: string) => void;
  disabled?: boolean;
  error?: string | null;
  isLocked?: boolean;
  lockedMinutesLeft?: number;
  className?: string;
}

export function SixBoxCodeInput({
  value,
  onChange,
  onComplete,
  disabled = false,
  error = null,
  isLocked = false,
  lockedMinutesLeft = 15,
  className
}: SixBoxCodeInputProps) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Array of 6 characters
  const digits = Array.from({ length: 6 }, (_, i) => value[i] || '');

  // Focus first empty box on mount if not disabled
  useEffect(() => {
    if (!disabled && !isLocked && inputRefs.current[0]) {
      const firstEmpty = digits.findIndex(d => d === '');
      const idxToFocus = firstEmpty === -1 ? 5 : firstEmpty;
      inputRefs.current[idxToFocus]?.focus();
    }
  }, [disabled, isLocked]);

  const handleChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled || isLocked) return;
    const inputChar = e.target.value.replace(/[^0-9]/g, '');
    if (!inputChar) {
      // Cleared
      const newDigits = [...digits];
      newDigits[index] = '';
      const newCode = newDigits.join('');
      onChange(newCode);
      return;
    }

    const char = inputChar.slice(-1);
    const newDigits = [...digits];
    newDigits[index] = char;
    const newCode = newDigits.join('');
    onChange(newCode);

    // Auto-advance
    if (index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    if (newCode.length === 6 && onComplete) {
      onComplete(newCode);
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled || isLocked) return;

    if (e.key === 'Backspace') {
      if (!digits[index] && index > 0) {
        // Move back and clear previous
        const newDigits = [...digits];
        newDigits[index - 1] = '';
        onChange(newDigits.join(''));
        inputRefs.current[index - 1]?.focus();
      } else {
        const newDigits = [...digits];
        newDigits[index] = '';
        onChange(newDigits.join(''));
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    if (disabled || isLocked) return;
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/[^0-9]/g, '').slice(0, 6);
    if (!pasted) return;

    onChange(pasted);
    const focusIndex = Math.min(pasted.length, 5);
    inputRefs.current[focusIndex]?.focus();

    if (pasted.length === 6 && onComplete) {
      onComplete(pasted);
    }
  };

  return (
    <div className={cn("w-full space-y-3", className)}>
      <div 
        className={cn(
          "flex items-center justify-between gap-1.5 sm:gap-2.5",
          error && "animate-shake"
        )}
      >
        {Array.from({ length: 6 }).map((_, i) => {
          const val = digits[i] || '';
          const isFilled = !!val;

          return (
            <input
              key={i}
              ref={(el) => { inputRefs.current[i] = el; }}
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={1}
              autoComplete={i === 0 ? "one-time-code" : "off"}
              aria-label={`Digit ${i + 1} of 6`}
              value={val}
              disabled={disabled || isLocked}
              onChange={(e) => handleChange(i, e)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              onPaste={handlePaste}
              className={cn(
                "w-11 h-12 sm:w-12 sm:h-14 text-center text-lg sm:text-xl font-bold rounded-xl transition-all duration-200 outline-none select-none",
                // Glass styling
                "bg-white/5 border border-white/10 text-white placeholder:text-white/20",
                "focus:bg-white/10 focus:border-[var(--ragaa-saffron,#F2A900)] focus:ring-2 focus:ring-[var(--ragaa-saffron,#F2A900)]/30",
                isFilled && "border-white/30 bg-white/10 text-[var(--ragaa-mint-white,#DDE6E1)]",
                error && "border-red-500/80 focus:border-red-500 focus:ring-red-500/30",
                isLocked && "opacity-40 cursor-not-allowed border-red-500/40"
              )}
            />
          );
        })}
      </div>

      {/* Live Error and Lock Messages with aria-live */}
      <div aria-live="assertive" className="min-h-[20px] text-center">
        {isLocked ? (
          <p className="text-xs text-red-400 font-medium">
            Account temporarily locked due to too many failed attempts. Try again in {lockedMinutesLeft} minutes.
          </p>
        ) : error ? (
          <p className="text-xs text-red-400 font-medium">
            {error}
          </p>
        ) : null}
      </div>
    </div>
  );
}

export default SixBoxCodeInput;
