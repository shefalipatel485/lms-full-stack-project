import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { formatDate } from "../utils/formatters";

export default function AttendancePage() {
  const { user } = useAuth();
  const [data, setData] = useState({ summary: {}, records: [] });
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().split("T")[0]);
  const [statuses, setStatuses] = useState({});
  const [savedMsg, setSavedMsg] = useState("");

  const loadAttendance = () => {
    api.get("/api/attendance").then((res) => setData(res.data));
  };

  useEffect(() => {
    loadAttendance();
    if (user?.role !== "student") {
      api.get("/api/batches").then((res) => {
        setBatches(res.data);
        if (res.data.length > 0) setSelectedBatch(res.data[0]);
      });
    }
  }, []);

  const saveAttendance = async () => {
    if (!selectedBatch) return;
    const records = selectedBatch.roster.map((stu) => ({
      student_id: stu.id,
      status: statuses[stu.id] || "Present",
    }));
    const res = await api.post("/api/attendance", {
      batch_id: selectedBatch.id,
      session_date: sessionDate,
      records,
    });
    setSavedMsg(res.data.message);
    loadAttendance();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Attendance Management</h1>
        <p className="text-sm text-slate-500">
          Overall Attendance Rate: <strong>{data.summary.attendance_percentage ?? 0}%</strong> ({data.summary.present_classes ?? 0}/{data.summary.total_eligible_classes ?? 0} classes)
        </p>
      </div>

      {user?.role !== "student" && selectedBatch && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
          <h2 className="font-bold text-slate-900">Record Batch Attendance</h2>
          {savedMsg && <p className="text-sm text-emerald-700 bg-emerald-50 p-2.5 rounded">{savedMsg}</p>}
          <div className="flex flex-wrap gap-3">
            <select
              value={selectedBatch.id}
              onChange={(e) => setSelectedBatch(batches.find((b) => b.id === Number(e.target.value)))}
              className="border rounded-lg px-3 py-2 text-sm"
            >
              {batches.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
            <input
              type="date"
              value={sessionDate}
              onChange={(e) => setSessionDate(e.target.value)}
              className="border rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div className="divide-y">
            {selectedBatch.roster.map((stu) => (
              <div key={stu.id} className="py-2.5 flex items-center justify-between text-sm">
                <span>{stu.full_name} ({stu.email})</span>
                <select
                  value={statuses[stu.id] || "Present"}
                  onChange={(e) => setStatuses({ ...statuses, [stu.id]: e.target.value })}
                  className="border rounded px-2 py-1 text-xs"
                >
                  <option value="Present">Present</option>
                  <option value="Absent">Absent</option>
                  <option value="Approved Leave">Approved Leave</option>
                </select>
              </div>
            ))}
          </div>

          <button onClick={saveAttendance} className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg">
            Save Attendance
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 border-b text-slate-600">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Batch ID</th>
              <th className="px-4 py-3">Student ID</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data.records.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-3">{formatDate(r.session_date)}</td>
                <td className="px-4 py-3">Batch #{r.batch_id}</td>
                <td className="px-4 py-3">Student #{r.student_id}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${r.status === "Present" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
                    {r.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
