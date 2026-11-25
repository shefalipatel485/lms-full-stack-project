import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import { formatCurrencyINR } from "../utils/formatters";
import { ArrowLeft, Video, FileText } from "lucide-react";

export default function CourseDetailPage() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);

  useEffect(() => {
    api.get(`/api/courses/${id}`).then((res) => setCourse(res.data));
  }, [id]);

  if (!course) return <div className="text-slate-500">Loading course details...</div>;

  return (
    <div className="space-y-6">
      <Link to="/courses" className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900">
        <ArrowLeft className="w-4 h-4" /> Back to Courses
      </Link>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <span className="text-xs font-bold px-2.5 py-1 rounded bg-indigo-50 text-indigo-700">{course.code}</span>
        <h1 className="text-2xl font-bold text-slate-900 mt-2">{course.title}</h1>
        <p className="text-slate-600 mt-2">{course.description}</p>
        <div className="flex flex-wrap gap-6 mt-4 text-sm text-slate-600">
          <span>Instructor: <strong>{course.instructor_name}</strong></span>
          <span>Duration: <strong>{course.duration_weeks} Weeks</strong></span>
          <span>Fee: <strong>{formatCurrencyINR(course.fee)}</strong></span>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900">Course Modules & Syllabus</h2>
        {course.modules.length === 0 && (
          <p className="text-sm text-slate-500 bg-white p-5 rounded-xl border">No modules published yet.</p>
        )}
        {course.modules.map((mod) => (
          <div key={mod.id} className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-bold text-slate-900">{mod.title}</h3>
            {mod.description && <p className="text-sm text-slate-500 mt-0.5">{mod.description}</p>}
            <div className="mt-4 divide-y divide-slate-100">
              {mod.lectures.map((lec) => (
                <div key={lec.id} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Video className="w-4 h-4 text-indigo-600" />
                    <div>
                      <p className="text-sm font-medium text-slate-800">{lec.title}</p>
                      <p className="text-xs text-slate-400">{lec.duration_minutes} mins</p>
                    </div>
                  </div>
                  <Link to="/lectures" className="text-xs font-semibold text-indigo-600 hover:underline">
                    Open Lecture
                  </Link>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
