import Link from "next/link";
import { Activity, ShieldCheck, Zap, BrainCircuit, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-b from-primary/10 via-background to-background">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center space-y-8 text-center">
            <div className="space-y-4 max-w-3xl">
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
                Understand Your Symptoms with <span className="text-primary text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400">AI Precision</span>
              </h1>
              <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Describe how you're feeling in natural language. Our advanced AI model analyzes your symptoms and provides instant, actionable health insights.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
              <Link
                href="/symptoms"
                className="inline-flex h-12 items-center justify-center rounded-full bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 hover:scale-105 active:scale-95 duration-200"
              >
                Check Symptoms Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <Link
                href="/auth/register"
                className="inline-flex h-12 items-center justify-center rounded-full border border-input bg-background px-8 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground hover:scale-105 active:scale-95 duration-200"
              >
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-secondary/30">
        <div className="container mx-auto px-4 md:px-6">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-3">
            <div className="flex flex-col items-center space-y-4 text-center group">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110">
                <BrainCircuit className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">Advanced AI Model</h3>
              <p className="text-muted-foreground">
                Powered by BART zero-shot classification to understand natural language symptom descriptions accurately.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 text-center group">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110">
                <Zap className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">Instant Results</h3>
              <p className="text-muted-foreground">
                Get immediate insights, severity assessments, and recommendations without waiting.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 text-center group sm:col-span-2 lg:col-span-1">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110">
                <ShieldCheck className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">Private & Secure</h3>
              <p className="text-muted-foreground">
                Your health data is encrypted and secure. Create an account to securely save your symptom history.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
