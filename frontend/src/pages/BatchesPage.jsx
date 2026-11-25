import React, { useEffect, useState } from "react";
import api from "../services/api";
import { formatDate } from "../utils/formatters";

export default function BatchesPage() {
  const [batches, setBatches] = useState([]);

  useEffect(() => {
    api.get("/api/batches").then((res) => setBatches(res.data));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Batch Management</h1>
        <p className="text-sm text-slate-500">Schedules, capacity, and enrolled student rosters</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-semibold">Batch Name</th>
                <th className="px-4 py-3 font-semibold">Course</th>
                <th className="px-4 py-3 font-semibold">Instructor</th>
                <th className="px-4 py-3 font-semibold">Schedule</th>
                <th className="px-4 py-3 font-semibold">Dates</th>
                <th className="px-4 py-3 font-semibold">Seats</th>
                <th className="px-4 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {batches.map((b) => (
                <tr key={b.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-semibold text-slate-900">{b.name}</td>
                  <td className="px-4 py-3">{b.course_title}</td>
                  <td className="px-4 py-3">{b.instructor_name}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{b.schedule_timing}</td>
                  <td className="px-4 py-3 text-xs">{formatDate(b.start_date)} – {formatDate(b.end_date)}</td>
                  <td className="px-4 py-3 font-medium">{b.enrolled_count} / {b.capacity}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-50 text-emerald-700">
                      {b.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
