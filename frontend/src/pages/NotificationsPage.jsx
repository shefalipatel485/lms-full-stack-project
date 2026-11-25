import React, { useEffect, useState } from "react";
import api from "../services/api";
import { formatDate } from "../utils/formatters";
import { Bell, Megaphone } from "lucide-react";

export default function NotificationsPage() {
  const [data, setData] = useState({ notifications: [], announcements: [] });

  useEffect(() => {
    api.get("/api/notifications").then((res) => setData(res.data));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Notifications & Announcements</h1>
        <p className="text-sm text-slate-500">Institute broadcasts and personal academic alerts</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3">
          <h2 className="font-bold text-slate-900 flex items-center gap-2">
            <Megaphone className="w-5 h-5 text-indigo-600" /> Institute Announcements
          </h2>
          {data.announcements.map((a) => (
            <div key={a.id} className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <p className="font-semibold text-sm text-slate-900">{a.title}</p>
              <p className="text-xs text-slate-600 mt-1">{a.content}</p>
              <p className="text-[11px] text-slate-400 mt-2">Target: {a.target_role} • {formatDate(a.created_at)}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3">
          <h2 className="font-bold text-slate-900 flex items-center gap-2">
            <Bell className="w-5 h-5 text-emerald-600" /> Personal Alerts
          </h2>
          {data.notifications.length === 0 && <p className="text-sm text-slate-400">No personal notifications.</p>}
          {data.notifications.map((n) => (
            <div key={n.id} className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <p className="font-semibold text-sm text-slate-900">{n.title}</p>
              <p className="text-xs text-slate-600 mt-1">{n.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
