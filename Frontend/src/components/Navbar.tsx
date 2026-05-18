"use client";

import Link from "next/link";
import { useTheme } from "next-themes";
import { Moon, Sun, Activity, Menu, X } from "lucide-react";
import { useState, useEffect } from "react";

export function Navbar() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Prevent hydration mismatch by only rendering theme toggle after mount
  useEffect(() => setMounted(true), []);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <Activity className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl hidden sm:inline-block">HelloHealth</span>
        </Link>
        
        {/* Desktop Nav */}
        <div className="hidden md:flex items-center space-x-6 text-sm font-medium">
          <Link href="/symptoms" className="transition-colors hover:text-primary">
            Symptom Checker
          </Link>
          <Link href="/history" className="transition-colors hover:text-primary text-muted-foreground">
            History
          </Link>
          <Link href="/dashboard" className="transition-colors hover:text-primary text-muted-foreground">
            Dashboard
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/auth/login" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              Login
            </Link>
            <Link 
              href="/auth/register" 
              className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
            >
              Sign Up
            </Link>
          </div>
          
          {mounted && (
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="inline-flex items-center justify-center rounded-md w-9 h-9 border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              aria-label="Toggle theme"
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            </button>
          )}

          {/* Mobile Menu Toggle */}
          <button 
            className="md:hidden p-2"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Nav */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t p-4 space-y-4 bg-background">
          <Link href="/symptoms" className="block text-sm font-medium" onClick={() => setIsMobileMenuOpen(false)}>Symptom Checker</Link>
          <Link href="/history" className="block text-sm font-medium" onClick={() => setIsMobileMenuOpen(false)}>History</Link>
          <Link href="/dashboard" className="block text-sm font-medium" onClick={() => setIsMobileMenuOpen(false)}>Dashboard</Link>
          <hr className="my-2 border-border" />
          <Link href="/auth/login" className="block text-sm font-medium" onClick={() => setIsMobileMenuOpen(false)}>Login</Link>
          <Link href="/auth/register" className="block text-sm font-medium text-primary" onClick={() => setIsMobileMenuOpen(false)}>Sign Up</Link>
        </div>
      )}
    </nav>
  );
}
