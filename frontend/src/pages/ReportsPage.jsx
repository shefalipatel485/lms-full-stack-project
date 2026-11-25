import React, { useEffect, useState } from "react";
import api from "../services/api";
import { Download } from "lucide-react";

export default function ReportsPage() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.get("/api/reports/dashboard").then((res) => setSummary(res.data));
  }, []);

  const exportCSV = () => {
    if (!summary?.chart_data) return;
    const rows = [
      Object.keys(summary.chart_data[0] || {}).join(","),
      ...summary.chart_data.map((r) => Object.values(r).join(",")),
    ].join("\n");
    const blob = new Blob([rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "lms_academic_report.csv";
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Operational & Academic Reports</h1>
          <p className="text-sm text-slate-500">Exportable analytics for management and instructors</p>
        </div>
        <button
          onClick={exportCSV}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg"
        >
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      {summary && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-bold text-slate-900 mb-3">Live KPI Snapshot</h2>
          <pre className="bg-slate-50 p-4 rounded-lg text-xs overflow-x-auto">
            {JSON.stringify(summary, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
