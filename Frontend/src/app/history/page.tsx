"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Loader2, Activity, Clock, ChevronLeft, ChevronRight, CheckCircle2 } from "lucide-react";
import { toast, Toaster } from "react-hot-toast";

interface HistoryItem {
  id: string;
  symptoms_text: string;
  diagnosis: string;
  confidence: number;
  severity: string;
  created_at: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchHistory = async (pageNumber: number) => {
    setLoading(true);
    try {
      const response = await api.get(`/history?page=${pageNumber}&limit=10`);
      setHistory(response.data.data.items);
      setTotalPages(response.data.data.pages);
      setPage(pageNumber);
    } catch (error: any) {
      toast.error(error.message || "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(1);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "mild": return "text-green-600 dark:text-green-400";
      case "moderate": return "text-yellow-600 dark:text-yellow-400";
      case "severe": return "text-red-600 dark:text-red-400";
      default: return "text-slate-600 dark:text-slate-400";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <Toaster position="top-right" />
      
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Your Symptom History</h1>
        <p className="text-muted-foreground mt-2">
          Review your past symptom checks and health insights.
        </p>
      </div>

      {loading && history.length === 0 ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : history.length === 0 ? (
        <div className="bg-card border rounded-xl p-12 text-center shadow-sm">
          <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium">No history yet</h3>
          <p className="text-muted-foreground mt-2">
            Your symptom checks will appear here once you've analyzed some symptoms.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div key={item.id} className="bg-card border rounded-xl p-6 shadow-sm transition-all hover:shadow-md">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    {new Date(item.created_at).toLocaleDateString()} at {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <p className="text-foreground italic">"{item.symptoms_text}"</p>
                </div>
                
                <div className="bg-secondary/50 p-4 rounded-lg md:w-1/3 shrink-0">
                  <h4 className="font-bold flex items-center gap-2">
                    <Activity className="h-4 w-4 text-primary" />
                    {item.diagnosis}
                  </h4>
                  <div className="flex items-center gap-4 mt-2 text-sm">
                    <span className={`font-semibold uppercase ${getSeverityColor(item.severity)}`}>
                      {item.severity}
                    </span>
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <CheckCircle2 className="h-3 w-3" />
                      {(item.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 pt-6">
              <button
                onClick={() => fetchHistory(page - 1)}
                disabled={page === 1 || loading}
                className="p-2 border rounded-md hover:bg-secondary disabled:opacity-50 disabled:pointer-events-none"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <span className="text-sm font-medium">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => fetchHistory(page + 1)}
                disabled={page === totalPages || loading}
                className="p-2 border rounded-md hover:bg-secondary disabled:opacity-50 disabled:pointer-events-none"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
