import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { GraduationCap, Lock, Mail, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@lms.edu");
  const [password, setPassword] = useState("Admin@123");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please check credentials.");
    }
  };

  const quickFill = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="flex flex-col items-center text-center mb-6">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl mb-3">
            <GraduationCap className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">EduSphere LMS</h1>
          <p className="text-sm text-slate-500 mt-1">Sign in to access your role-based academic workspace</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="you@lms.edu"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {loading ? "Authenticating..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-slate-200">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2.5 text-center">
            Quick Demo Role Login
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => quickFill("admin@lms.edu", "Admin@123")}
              className="py-1.5 px-2 text-xs font-medium rounded-lg border border-slate-200 hover:bg-indigo-50 hover:border-indigo-300 text-slate-700"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => quickFill("instructor@lms.edu", "Instructor@123")}
              className="py-1.5 px-2 text-xs font-medium rounded-lg border border-slate-200 hover:bg-indigo-50 hover:border-indigo-300 text-slate-700"
            >
              Instructor
            </button>
            <button
              type="button"
              onClick={() => quickFill("student@lms.edu", "Student@123")}
              className="py-1.5 px-2 text-xs font-medium rounded-lg border border-slate-200 hover:bg-indigo-50 hover:border-indigo-300 text-slate-700"
            >
              Student
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
