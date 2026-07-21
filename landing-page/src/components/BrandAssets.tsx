import React from "react";
import { Sun, Moon } from "lucide-react";

// Import custom brand asset images from root directory
import logoLight from "../../vendoriq logo light.png";
import logoDark from "../../vendoriq logo dark.png";
import fullLight from "../../vendoriq light mode.png";
import fullDark from "../../vendoriq dark mode.png";

export function BrandLogo({ className = "w-7 h-7", theme = "dark" }: { className?: string; theme?: "dark" | "light" }) {
  const isLight = theme === "light";
  const src = isLight ? logoLight : logoDark;
  
  // mix-blend-multiply removes white background for light mode
  // mix-blend-screen removes black background for dark mode
  const blendClass = isLight ? "mix-blend-multiply" : "mix-blend-screen";

  return (
    <img 
      src={src} 
      alt="VendorIQ Logo Mark" 
      className={`${className} transition-transform duration-300 hover:scale-105 object-contain ${blendClass}`} 
      referrerPolicy="no-referrer"
    />
  );
}

export function BrandFullLogo({ className = "w-6 h-6 sm:w-7 sm:h-7", theme = "dark", textClassName = "text-base sm:text-lg md:text-xl" }: { className?: string; theme?: "dark" | "light"; textClassName?: string }) {
  return (
    <div className="flex items-center gap-1.5 sm:gap-2 group cursor-pointer select-none">
      <BrandLogo className={className} theme={theme} />
      <span className={`font-display font-black tracking-tight leading-none ${textClassName}`}>
        <span className="text-[var(--text)] transition-colors duration-200 group-hover:text-emerald-400">Vendor</span>
        <span className="text-[var(--green)]">IQ</span>
      </span>
    </div>
  );
}

interface ThemeToggleProps {
  theme: "dark" | "light";
  onToggle: () => void;
}

export function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="relative flex items-center justify-between w-12 h-6 sm:w-14 sm:h-7 rounded-full p-0.5 sm:p-1 cursor-pointer transition-all duration-300 border border-[var(--green-border)] bg-[var(--green-dim)] shrink-0"
      title="Toggle Light/Dark Theme"
    >
      {/* Sliding indicator */}
      <div 
        className={`absolute top-0.5 bottom-0.5 w-4.5 h-4.5 sm:w-5.5 sm:h-5.5 rounded-full bg-gradient-to-tr from-emerald-500 to-cyan-400 shadow-[0_2px_8px_rgba(16,185,129,0.3)] transition-all duration-300 flex items-center justify-center ${
          theme === "light" ? "left-[24px] sm:left-[28px]" : "left-0.5"
        }`}
      >
        {theme === "dark" ? (
          <Moon className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-black" />
        ) : (
          <Sun className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-black" />
        )}
      </div>

      {/* Background Icons */}
      <div className="flex justify-between items-center w-full px-1 pointer-events-none select-none text-[var(--green)]">
        <Moon className={`w-3 h-3 sm:w-3.5 sm:h-3.5 transition-opacity duration-300 ${theme === "dark" ? "opacity-20" : "opacity-80"}`} />
        <Sun className={`w-3 h-3 sm:w-3.5 sm:h-3.5 transition-opacity duration-300 ${theme === "light" ? "opacity-20" : "opacity-80"}`} />
      </div>
    </button>
  );
}
