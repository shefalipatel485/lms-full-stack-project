import React, { useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function ProfilePage() {
  const { user } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/api/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setStatusMsg(res.data.message);
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setStatusMsg(err.response?.data?.detail || "Error updating password");
    }
  };

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Profile & Account Security</h1>
        <p className="text-sm text-slate-500">Manage your personal details and password</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-2 text-sm">
        <p>Full Name: <strong>{user?.full_name}</strong></p>
        <p>Email Address: <strong>{user?.email}</strong></p>
        <p>Assigned Role: <strong className="capitalize">{user?.role}</strong></p>
      </div>

      <form onSubmit={handlePasswordChange} className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        <h2 className="font-bold text-slate-900">Change Password</h2>
        {statusMsg && <p className="text-sm text-indigo-700 bg-indigo-50 p-2.5 rounded">{statusMsg}</p>}
        <input
          type="password"
          required
          placeholder="Current Password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 text-sm"
        />
        <input
          type="password"
          required
          minLength={6}
          placeholder="New Password (min 6 chars)"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 text-sm"
        />
        <button type="submit" className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg">
          Update Password
        </button>
      </form>
    </div>
  );
}
