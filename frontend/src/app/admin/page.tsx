"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Users,
  TrendingUp,
  CreditCard,
  DollarSign,
  Activity,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Eye,
  Ban,
  Star,
} from "lucide-react";
import { adminApi } from "@/lib/api";

interface PlatformStats {
  total_users: number;
  total_strategies: number;
  total_builds_completed: number;
  total_credits_purchased: number;
  total_marketplace_sales: number;
  revenue_30d: number;
  active_users_24h: number;
  top_strategies: Array<{
    name: string;
    completions: number;
    avg_performance: number;
  }>;
}

interface UserSummary {
  id: string;
  email: string;
  full_name: string | null;
  credits_balance: number;
  is_admin: boolean;
  total_builds: number;
  total_spent_credits: number;
  created_at: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "users" | "listings">(
    "overview"
  );

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    // Check if admin
    const userData = localStorage.getItem("user");
    if (!userData) {
      router.push("/login");
      return;
    }

    try {
      const user = JSON.parse(userData);
      if (!user.is_admin) {
        router.push("/");
        return;
      }
    } catch {
      router.push("/login");
      return;
    }

    loadData();
  }, [router]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.getUsers(50, 0),
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      console.error("Failed to load admin data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureListing = async (listingId: string) => {
    try {
      await adminApi.featureListing(listingId);
      alert("Listing featured successfully");
    } catch (error) {
      console.error("Failed to feature listing:", error);
      alert("Failed to feature listing");
    }
  };

  const handleSuspendListing = async (listingId: string) => {
    if (!confirm("Are you sure you want to suspend this listing?")) return;
    try {
      await adminApi.suspendListing(listingId);
      alert("Listing suspended successfully");
    } catch (error) {
      console.error("Failed to suspend listing:", error);
      alert("Failed to suspend listing");
    }
  };

  const handleDeactivateUser = async (userId: string) => {
    if (!confirm("Are you sure you want to deactivate this user?")) return;
    try {
      await adminApi.deactivateUser(userId);
      loadData();
      alert("User deactivated successfully");
    } catch (error) {
      console.error("Failed to deactivate user:", error);
      alert("Failed to deactivate user");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">Platform Management</span>
              <button
                onClick={() => router.push("/")}
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                Back to App
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="border-b border-gray-800 mb-8">
          <nav className="flex gap-8">
            {["overview", "users", "listings"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as typeof activeTab)}
                className={`pb-4 px-1 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-gray-400 hover:text-gray-300"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && stats && (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Users"
                value={stats.total_users.toLocaleString()}
                change="+12%"
                positive={true}
                icon={Users}
              />
              <StatCard
                title="Strategies Built"
                value={stats.total_strategies.toLocaleString()}
                change="+8%"
                positive={true}
                icon={TrendingUp}
              />
              <StatCard
                title="Revenue (30d)"
                value={`$${stats.revenue_30d.toLocaleString()}`}
                change="+23%"
                positive={true}
                icon={DollarSign}
              />
              <StatCard
                title="Active Users (24h)"
                value={stats.active_users_24h.toLocaleString()}
                change="-3%"
                positive={false}
                icon={Activity}
              />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <CreditCard className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Credits Purchased</p>
                    <p className="text-2xl font-bold text-white">
                      {stats.total_credits_purchased.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Builds Completed</p>
                    <p className="text-2xl font-bold text-white">
                      {stats.total_builds_completed.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Marketplace Sales</p>
                    <p className="text-2xl font-bold text-white">
                      {stats.total_marketplace_sales.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Top Strategies */}
            <div className="bg-gray-900 rounded-lg border border-gray-800">
              <div className="p-6 border-b border-gray-800">
                <h3 className="text-lg font-semibold text-white">
                  Top Performing Strategies
                </h3>
              </div>
              <div className="divide-y divide-gray-800">
                {stats.top_strategies.map((strategy, index) => (
                  <div
                    key={index}
                    className="p-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <span className="text-sm font-bold text-blue-400">
                          {index + 1}
                        </span>
                      </div>
                      <div>
                        <p className="text-white font-medium">{strategy.name}</p>
                        <p className="text-sm text-gray-400">
                          {strategy.completions} builds
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-white font-semibold">
                        {strategy.avg_performance.toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-400">avg performance</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="bg-gray-900 rounded-lg border border-gray-800">
            <div className="p-6 border-b border-gray-800 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">User Management</h3>
              <span className="text-sm text-gray-400">
                {users.length} users total
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Credits
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Builds
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Spent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Joined
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-800/50">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-300">
                              {user.full_name?.charAt(0) || user.email.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <p className="text-white font-medium">
                              {user.full_name || "No name"}
                            </p>
                            <p className="text-sm text-gray-400">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-white">
                        {user.credits_balance.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-white">
                        {user.total_builds}
                      </td>
                      <td className="px-6 py-4 text-white">
                        {user.total_spent_credits.toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        {user.is_admin ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400">
                            Admin
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-500/20 text-gray-400">
                            User
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-400 text-sm">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button className="text-gray-400 hover:text-blue-400 transition-colors">
                            <Eye className="w-4 h-4" />
                          </button>
                          {!user.is_admin && (
                            <button
                              onClick={() => handleDeactivateUser(user.id)}
                              className="text-gray-400 hover:text-red-400 transition-colors"
                            >
                              <Ban className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Listings Tab */}
        {activeTab === "listings" && (
          <div className="bg-gray-900 rounded-lg border border-gray-800">
            <div className="p-6 border-b border-gray-800">
              <h3 className="text-lg font-semibold text-white">
                Marketplace Listings
              </h3>
              <p className="text-sm text-gray-400 mt-1">
                Manage bot listings and marketplace content
              </p>
            </div>
            <div className="p-12 text-center">
              <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-gray-600" />
              </div>
              <p className="text-gray-400 mb-4">
                Listing management features coming soon
              </p>
              <p className="text-sm text-gray-500">
                View individual listing details and manage featured/suspended listings
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({
  title,
  value,
  change,
  positive,
  icon: Icon,
}: {
  title: string;
  value: string;
  change: string;
  positive: boolean;
  icon: any;
}) {
  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <div className="flex items-center justify-between mb-4">
        <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
          <Icon className="w-5 h-5 text-blue-400" />
        </div>
        <div
          className={`flex items-center gap-1 text-sm font-medium ${
            positive ? "text-emerald-400" : "text-red-400"
          }`}
        >
          {positive ? (
            <ArrowUpRight className="w-4 h-4" />
          ) : (
            <ArrowDownRight className="w-4 h-4" />
          )}
          {change}
        </div>
      </div>
      <p className="text-gray-400 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  );
}
