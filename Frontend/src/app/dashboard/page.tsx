"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Loader2, Activity, User, FileText, TrendingUp, AlertTriangle } from "lucide-react";
import { toast, Toaster } from "react-hot-toast";

interface UserProfile {
  username: string;
  email: string;
  created_at: string;
}

interface Stats {
  total: number;
  recent: any[];
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch profile
        const profileRes = await api.get("/auth/me");
        setProfile(profileRes.data.data);

        // Fetch recent history for stats
        const historyRes = await api.get("/history?page=1&limit=5");
        setStats({
          total: historyRes.data.data.total,
          recent: historyRes.data.data.items,
        });
      } catch (error: any) {
        toast.error("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-4rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Toaster position="top-right" />
      
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back, {profile?.username || "User"}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {/* Profile Card */}
        <div className="bg-card border rounded-xl p-6 shadow-sm flex flex-col gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-primary/10 p-3 rounded-full">
              <User className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold">{profile?.username}</h3>
              <p className="text-sm text-muted-foreground">{profile?.email}</p>
            </div>
          </div>
          <div className="text-xs text-muted-foreground mt-auto">
            Member since {profile ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
          </div>
        </div>

        {/* Stats Card */}
        <div className="bg-card border rounded-xl p-6 shadow-sm flex flex-col gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-blue-500/10 p-3 rounded-full">
              <FileText className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Total Checks</h3>
              <p className="text-2xl font-bold">{stats?.total || 0}</p>
            </div>
          </div>
          <div className="text-xs text-muted-foreground mt-auto flex items-center gap-1">
            <TrendingUp className="h-3 w-3" /> Lifetime symptom queries
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
      <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
        {stats?.recent && stats.recent.length > 0 ? (
          <div className="divide-y">
            {stats.recent.map((item) => (
              <div key={item.id} className="p-4 flex flex-col sm:flex-row justify-between sm:items-center gap-4 hover:bg-muted/50 transition-colors">
                <div>
                  <h4 className="font-medium flex items-center gap-2">
                    <Activity className="h-4 w-4 text-primary" />
                    {item.diagnosis}
                  </h4>
                  <p className="text-sm text-muted-foreground truncate max-w-md mt-1">
                    "{item.symptoms_text}"
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0 text-sm">
                  <span className="px-2 py-1 bg-secondary rounded text-xs font-medium uppercase">
                    {item.severity}
                  </span>
                  <span className="text-muted-foreground">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-muted-foreground">
            No recent activity found. Head over to the Symptom Checker to get started.
          </div>
        )}
      </div>
    </div>
  );
}
