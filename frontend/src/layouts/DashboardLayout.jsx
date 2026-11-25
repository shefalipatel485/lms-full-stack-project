import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard, BookOpen, Users, Layers, Video, FileText,
  HelpCircle, CalendarCheck, CreditCard, Award, UserCircle,
  BarChart3, Bell, LogOut, Menu, X, GraduationCap
} from "lucide-react";

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const role = user?.role || "student";

  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "instructor", "student"] },
    { to: "/courses", label: "Courses", icon: BookOpen, roles: ["admin", "instructor", "student"] },
    { to: "/batches", label: "Batches", icon: Layers, roles: ["admin", "instructor", "student"] },
    { to: "/lectures", label: "Lectures & Notes", icon: Video, roles: ["admin", "instructor", "student"] },
    { to: "/assignments", label: "Assignments", icon: FileText, roles: ["admin", "instructor", "student"] },
    { to: "/quizzes", label: "Quizzes", icon: HelpCircle, roles: ["admin", "instructor", "student"] },
    { to: "/attendance", label: "Attendance", icon: CalendarCheck, roles: ["admin", "instructor", "student"] },
    { to: "/payments", label: "Fees & Payments", icon: CreditCard, roles: ["admin", "student"] },
    { to: "/certificates", label: "Certificates", icon: Award, roles: ["admin", "student"] },
    { to: "/users", label: "Users & Rosters", icon: Users, roles: ["admin", "instructor"] },
    { to: "/reports", label: "Reports & Analytics", icon: BarChart3, roles: ["admin", "instructor"] },
    { to: "/notifications", label: "Announcements", icon: Bell, roles: ["admin", "instructor", "student"] },
    { to: "/profile", label: "Profile & Security", icon: UserCircle, roles: ["admin", "instructor", "student"] },
  ].filter((item) => item.roles.includes(role));

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-slate-900 text-slate-100 flex flex-col transition-transform duration-200 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <GraduationCap className="w-7 h-7 text-indigo-400" />
            <span className="font-bold text-lg tracking-tight">EduSphere LMS</span>
          </div>
          <button className="lg:hidden text-slate-400" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-600 text-white"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >
              <item.icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="mb-3">
            <p className="text-sm font-semibold text-white truncate">{user?.full_name}</p>
            <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium uppercase rounded bg-indigo-500/20 text-indigo-300">
              {role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-rose-300 hover:bg-rose-950/50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200 px-4 lg:px-8 flex items-center justify-between sticky top-0 z-10">
          <button
            className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="text-sm text-slate-500 hidden sm:block">
            Academic Portal • Role: <strong className="capitalize text-slate-800">{role}</strong>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
              API Connected
            </span>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
