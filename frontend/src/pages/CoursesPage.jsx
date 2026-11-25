import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { formatCurrencyINR } from "../utils/formatters";
import { Plus, Search, BookOpen } from "lucide-react";

export default function CoursesPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    code: "", title: "", description: "", category: "Software Engineering",
    duration_weeks: 8, fee: 15000, status: "Published"
  });

  const loadCourses = () => {
    api.get("/api/courses", { params: search ? { search } : {} }).then((res) => setCourses(res.data));
  };

  useEffect(() => {
    loadCourses();
  }, [search]);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post("/api/courses", form);
    setShowCreate(false);
    setForm({ code: "", title: "", description: "", category: "Software Engineering", duration_weeks: 8, fee: 15000, status: "Published" });
    loadCourses();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Course Catalogue</h1>
          <p className="text-sm text-slate-500">Manage and explore structured institute courses</p>
        </div>
        {user?.role === "admin" && (
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4" /> New Course
          </button>
        )}
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-white p-6 rounded-xl border border-slate-200 grid grid-cols-1 md:grid-cols-2 gap-4">
          <input required placeholder="Course Code (e.g. PY-301)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input required placeholder="Course Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input required placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input required type="number" placeholder="Fee (INR)" value={form.fee} onChange={(e) => setForm({ ...form, fee: Number(e.target.value) })} className="border rounded-lg px-3 py-2 text-sm" />
          <textarea required placeholder="Course Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="border rounded-lg px-3 py-2 text-sm md:col-span-2" />
          <div className="md:col-span-2 flex justify-end gap-2">
            <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-slate-600">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg">Save Course</button>
          </div>
        </form>
      )}

      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
        <input
          type="text"
          placeholder="Search courses by title or code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-lg text-sm"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {courses.map((course) => (
          <div key={course.id} className="bg-white rounded-xl border border-slate-200 p-5 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-indigo-50 text-indigo-700">{course.code}</span>
                <span className="text-xs font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">{course.status}</span>
              </div>
              <h3 className="text-lg font-bold text-slate-900">{course.title}</h3>
              <p className="text-sm text-slate-500 mt-1 line-clamp-2">{course.description}</p>
              <div className="mt-4 space-y-1 text-xs text-slate-600">
                <p>Instructor: <strong>{course.instructor_name}</strong></p>
                <p>Duration: <strong>{course.duration_weeks} Weeks</strong> • Fee: <strong>{formatCurrencyINR(course.fee)}</strong></p>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
              {user?.role === "student" && course.is_enrolled ? (
                <span className="text-xs font-semibold text-indigo-600">Progress: {course.progress_percent}%</span>
              ) : (
                <span className="text-xs text-slate-400">{course.enrolled_students_count} students</span>
              )}
              <Link
                to={`/courses/${course.id}`}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-600 hover:text-indigo-800"
              >
                <BookOpen className="w-4 h-4" /> View Modules
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
