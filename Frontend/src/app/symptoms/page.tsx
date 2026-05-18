"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Loader2, Search, AlertCircle, CheckCircle2, Info, Activity } from "lucide-react";
import { toast, Toaster } from "react-hot-toast";

interface SymptomResponse {
  diagnosis: string;
  confidence: number;
  severity: "mild" | "moderate" | "severe" | "unknown";
  source: string;
  symptoms: string[];
  recommendations: string[];
  when_to_see_doctor: string;
  disclaimer: string;
}

export default function SymptomsPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SymptomResponse | null>(null);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || query.length < 2) {
      toast.error("Please enter at least 2 characters.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await api.post("/symptoms/check", { symptoms: query });
      setResult(response.data);
      toast.success("Analysis complete");
    } catch (error: any) {
      toast.error(error.message || "Failed to analyze symptoms");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "mild": return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-900";
      case "moderate": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-900";
      case "severe": return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-900";
      default: return "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Toaster position="top-right" />
      
      <div className="mb-8 text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight md:text-4xl">Symptom Checker</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Describe how you're feeling. Our AI will analyze your symptoms and provide insights based on our medical knowledge base.
        </p>
      </div>

      <div className="bg-card rounded-xl shadow-sm border p-6 mb-8">
        <form onSubmit={handleCheck} className="space-y-4">
          <div className="relative">
            <textarea
              className="w-full min-h-[120px] p-4 pr-12 rounded-lg border bg-background text-foreground focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none transition-shadow"
              placeholder="E.g., I have a severe headache, my throat hurts, and I feel slightly feverish..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-3 bottom-3 p-2 bg-primary text-primary-foreground rounded-full shadow hover:bg-primary/90 transition-transform active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Search className="h-5 w-5" />}
            </button>
          </div>
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <Info className="h-3 w-3" />
            For educational purposes only. Not medical advice.
          </p>
        </form>
      </div>

      {result && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-card rounded-xl shadow-sm border overflow-hidden">
            <div className="p-6 border-b bg-muted/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
                  <Activity className="h-6 w-6 text-primary" />
                  {result.diagnosis}
                </h2>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getSeverityColor(result.severity)}`}>
                    {result.severity.toUpperCase()} SEVERITY
                  </span>
                  <span className="text-sm text-muted-foreground flex items-center gap-1">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    {(result.confidence * 100).toFixed(0)}% Match
                  </span>
                </div>
              </div>
              <div className="text-xs text-muted-foreground px-3 py-1 bg-secondary rounded-full self-start md:self-center">
                Source: {result.source.replace("_", " ").toUpperCase()}
              </div>
            </div>

            <div className="p-6 grid gap-6 md:grid-cols-2">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    Common Symptoms
                  </h3>
                  <ul className="space-y-2">
                    {result.symptoms.length > 0 ? result.symptoms.map((sym, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                        {sym}
                      </li>
                    )) : (
                      <p className="text-sm text-muted-foreground italic">No specific symptoms listed.</p>
                    )}
                  </ul>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                    Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {result.recommendations.length > 0 ? result.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 mt-1.5 shrink-0" />
                        {rec}
                      </li>
                    )) : (
                      <p className="text-sm text-muted-foreground italic">No specific recommendations.</p>
                    )}
                  </ul>
                </div>
              </div>
            </div>

            {result.when_to_see_doctor && (
              <div className="p-6 bg-red-500/10 border-t border-red-500/20 text-red-800 dark:text-red-300">
                <h3 className="font-semibold flex items-center gap-2 mb-1">
                  <AlertCircle className="h-4 w-4" />
                  When to see a doctor
                </h3>
                <p className="text-sm leading-relaxed">{result.when_to_see_doctor}</p>
              </div>
            )}
          </div>
          
          <p className="text-xs text-center text-muted-foreground max-w-2xl mx-auto italic">
            Disclaimer: {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
