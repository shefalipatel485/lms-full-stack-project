import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { formatDate } from "../utils/formatters";

export default function AssignmentsPage() {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [answerText, setAnswerText] = useState({});
  const [submissions, setSubmissions] = useState({});
  const [marks, setMarks] = useState({});
  const [feedback, setFeedback] = useState({});

  const loadAssignments = () => {
    api.get("/api/assignments").then((res) => setAssignments(res.data));
  };

  useEffect(() => {
    loadAssignments();
  }, []);

  const handleSubmitWork = async (assignmentId) => {
    await api.post("/api/submissions", {
      assignment_id: assignmentId,
      submission_text: answerText[assignmentId] || "Completed assignment deliverables.",
    });
    loadAssignments();
  };

  const loadSubmissions = async (assignmentId) => {
    const res = await api.get(`/api/assignments/${assignmentId}/submissions`);
    setSubmissions((prev) => ({ ...prev, [assignmentId]: res.data }));
  };

  const handleEvaluate = async (subId, assignmentId) => {
    await api.post(`/api/submissions/${subId}/evaluate`, {
      marks_obtained: Number(marks[subId] || 85),
      comments: feedback[subId] || "Good work.",
    });
    loadSubmissions(assignmentId);
    loadAssignments();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Assignments & Evaluations</h1>
        <p className="text-sm text-slate-500">Coursework deadlines, student submissions, and instructor grading</p>
      </div>

      <div className="space-y-4">
        {assignments.map((a) => (
          <div key={a.id} className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{a.title}</h3>
                <p className="text-sm text-slate-600 mt-1">{a.instructions}</p>
              </div>
              <div className="text-xs text-slate-500 shrink-0">
                <p>Max Marks: <strong>{a.max_marks}</strong></p>
                <p>Due: <strong>{formatDate(a.due_date)}</strong></p>
              </div>
            </div>

            {user?.role === "student" && (
              <div className="pt-3 border-t border-slate-100">
                {a.my_submission ? (
                  <div className="p-3 rounded-lg bg-slate-50 text-sm space-y-1">
                    <p>Status: <strong className="text-indigo-600">{a.my_submission.status}</strong></p>
                    <p className="text-slate-600">Your Answer: {a.my_submission.submission_text}</p>
                    {a.my_submission.marks_obtained !== null && (
                      <p className="text-emerald-700 font-semibold">
                        Score: {a.my_submission.marks_obtained} / {a.max_marks} — Feedback: {a.my_submission.comments}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="text"
                      placeholder="Enter GitHub repo link or solution summary..."
                      value={answerText[a.id] || ""}
                      onChange={(e) => setAnswerText({ ...answerText, [a.id]: e.target.value })}
                      className="flex-1 border rounded-lg px-3 py-2 text-sm"
                    />
                    <button
                      onClick={() => handleSubmitWork(a.id)}
                      className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700"
                    >
                      Submit Assignment
                    </button>
                  </div>
                )}
              </div>
            )}

            {(user?.role === "instructor" || user?.role === "admin") && (
              <div className="pt-3 border-t border-slate-100">
                <button
                  onClick={() => loadSubmissions(a.id)}
                  className="text-xs font-semibold text-indigo-600 hover:underline"
                >
                  View & Grade Submissions ({a.submissions_count})
                </button>

                {submissions[a.id]?.map((sub) => (
                  <div key={sub.id} className="mt-3 p-3 rounded-lg bg-slate-50 flex flex-col md:flex-row md:items-center justify-between gap-3 text-sm">
                    <div>
                      <p className="font-semibold">{sub.student_name} <span className="text-xs text-indigo-600">({sub.status})</span></p>
                      <p className="text-slate-600">{sub.submission_text}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        placeholder="Marks"
                        defaultValue={sub.marks_obtained ?? ""}
                        onChange={(e) => setMarks({ ...marks, [sub.id]: e.target.value })}
                        className="w-20 border rounded px-2 py-1 text-xs"
                      />
                      <input
                        type="text"
                        placeholder="Feedback"
                        defaultValue={sub.comments ?? ""}
                        onChange={(e) => setFeedback({ ...feedback, [sub.id]: e.target.value })}
                        className="border rounded px-2 py-1 text-xs"
                      />
                      <button
                        onClick={() => handleEvaluate(sub.id, a.id)}
                        className="px-3 py-1 bg-emerald-600 text-white text-xs font-medium rounded"
                      >
                        Save Grade
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
