import React, { useEffect, useState } from "react";
import api, { API_BASE_URL } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { CheckCircle, ExternalLink, FileDown, PlayCircle } from "lucide-react";

export default function LecturesPage() {
  const { user } = useAuth();
  const [lectures, setLectures] = useState([]);
  const [msg, setMsg] = useState("");

  const loadLectures = () => {
    api.get("/api/lectures").then((res) => setLectures(res.data));
  };

  useEffect(() => {
    loadLectures();
  }, []);

  const markComplete = async (lectureId) => {
    const res = await api.post(`/api/lectures/${lectureId}/complete`);
    setMsg(`Progress updated: ${res.data.course_progress_percent}%`);
    loadLectures();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Lectures & Study Materials</h1>
        <p className="text-sm text-slate-500">Watch recorded sessions, download study notes, and track completion</p>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm">
          {msg}
        </div>
      )}

      <div className="space-y-4">
        {lectures.map((lec) => (
          <div key={lec.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <PlayCircle className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-bold text-slate-900">{lec.title}</h3>
                  {lec.is_completed && (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                      <CheckCircle className="w-3.5 h-3.5" /> Completed
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-600 mt-1">{lec.description}</p>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {lec.video_url && (
                  <a
                    href={lec.video_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800"
                  >
                    <ExternalLink className="w-3.5 h-3.5" /> Watch Video
                  </a>
                )}
                {user?.role === "student" && !lec.is_completed && (
                  <button
                    onClick={() => markComplete(lec.id)}
                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
                  >
                    Mark Completed
                  </button>
                )}
              </div>
            </div>

            {lec.materials?.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
                {lec.materials.map((m) => (
                  <a
                    key={m.id}
                    href={m.file_url.startsWith("http") ? m.file_url : `${API_BASE_URL}${m.file_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-medium text-slate-700"
                  >
                    <FileDown className="w-3.5 h-3.5 text-indigo-600" />
                    {m.title} ({m.file_type})
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
