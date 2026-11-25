import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import StatCard from "../components/StatCard";
import { formatCurrencyINR } from "../utils/formatters";
import { Users, BookOpen, Layers, IndianRupee, Clock, Award, CheckCircle2 } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/reports/dashboard")
      .then((res) => setData(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-500 py-10">Loading dashboard metrics...</div>;
  if (!data) return <div className="text-rose-600">Unable to load dashboard data.</div>;

  const { role, kpis, chart_data } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Welcome back, {user?.full_name}</h1>
        <p className="text-sm text-slate-500">Live overview from database records</p>
      </div>

      {role === "admin" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Students" value={kpis.total_students} icon={Users} accent="indigo" />
          <StatCard title="Active Batches" value={kpis.active_batches} subtitle={`${kpis.total_courses} total courses`} icon={Layers} accent="sky" />
          <StatCard title="Collected Revenue" value={formatCurrencyINR(kpis.total_revenue)} icon={IndianRupee} accent="emerald" />
          <StatCard title="Pending Fees" value={formatCurrencyINR(kpis.pending_fees)} subtitle={`${kpis.pending_evaluations} evals pending`} icon={Clock} accent="amber" />
        </div>
      )}

      {role === "instructor" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Assigned Courses" value={kpis.assigned_courses} icon={BookOpen} accent="indigo" />
          <StatCard title="Assigned Batches" value={kpis.assigned_batches} icon={Layers} accent="sky" />
          <StatCard title="Active Students" value={kpis.total_students} icon={Users} accent="emerald" />
          <StatCard title="Pending Evaluations" value={kpis.pending_evaluations} icon={Clock} accent="amber" />
        </div>
      )}

      {role === "student" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Enrolled Courses" value={kpis.enrolled_courses} icon={BookOpen} accent="indigo" />
          <StatCard title="Attendance" value={`${kpis.attendance_percentage}%`} icon={CheckCircle2} accent="emerald" />
          <StatCard title="Avg. Course Progress" value={`${kpis.average_progress}%`} icon={Layers} accent="sky" />
          <StatCard title="Certificates Earned" value={kpis.certificates_earned} icon={Award} accent="amber" />
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900 mb-4">
          {role === "admin" && "Course Enrollment Distribution"}
          {role === "instructor" && "Batch Enrollment vs Capacity"}
          {role === "student" && "Course Completion Progress (%)"}
        </h2>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart_data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar
                dataKey={role === "student" ? "progress" : "students"}
                fill="#4f46e5"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
