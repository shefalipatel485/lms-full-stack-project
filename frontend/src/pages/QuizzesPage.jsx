import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function QuizzesPage() {
  const { user } = useAuth();
  const [quizzes, setQuizzes] = useState([]);
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [selected, setSelected] = useState({});
  const [result, setResult] = useState(null);

  const loadQuizzes = () => {
    api.get("/api/quizzes").then((res) => setQuizzes(res.data));
  };

  useEffect(() => {
    loadQuizzes();
  }, []);

  const submitQuiz = async () => {
    const answers = activeQuiz.questions.map((q) => ({
      question_id: q.id,
      selected_option_id: selected[q.id] || null,
    }));
    const res = await api.post(`/api/quizzes/${activeQuiz.id}/attempt`, { answers });
    setResult(res.data);
    setActiveQuiz(null);
    loadQuizzes();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">MCQ Quizzes & Examinations</h1>
        <p className="text-sm text-slate-500">Timed assessments with automated server-side evaluation</p>
      </div>

      {result && (
        <div className={`p-5 rounded-xl border ${result.passed ? "bg-emerald-50 border-emerald-200" : "bg-amber-50 border-amber-200"}`}>
          <h3 className="font-bold text-lg text-slate-900">
            Quiz Result: {result.score} / {result.total_marks} ({result.passed ? "PASSED" : "NEEDS IMPROVEMENT"})
          </h3>
          <p className="text-sm text-slate-600 mt-1">Passing Marks Required: {result.passing_marks}</p>
        </div>
      )}

      {activeQuiz ? (
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
          <div className="flex items-center justify-between border-b pb-4">
            <div>
              <h2 className="text-xl font-bold">{activeQuiz.title}</h2>
              <p className="text-xs text-slate-500">Duration: {activeQuiz.duration_minutes} mins • Total Marks: {activeQuiz.total_marks}</p>
            </div>
            <button onClick={() => setActiveQuiz(null)} className="text-sm text-slate-500">Cancel</button>
          </div>

          {activeQuiz.questions.map((q, idx) => (
            <div key={q.id} className="space-y-2">
              <p className="font-semibold text-slate-900">{idx + 1}. {q.question_text}</p>
              <div className="space-y-1.5 pl-4">
                {q.options.map((opt) => (
                  <label key={opt.id} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input
                      type="radio"
                      name={`q-${q.id}`}
                      checked={selected[q.id] === opt.id}
                      onChange={() => setSelected({ ...selected, [q.id]: opt.id })}
                    />
                    <span>{opt.option_text}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}

          <button
            onClick={submitQuiz}
            className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700"
          >
            Submit Quiz Attempt
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quizzes.map((q) => (
            <div key={q.id} className="bg-white rounded-xl border border-slate-200 p-5 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-lg text-slate-900">{q.title}</h3>
                <p className="text-sm text-slate-500 mt-1">{q.description}</p>
                <p className="text-xs text-slate-600 mt-3">
                  Questions: <strong>{q.questions_count}</strong> • Marks: <strong>{q.total_marks}</strong> • Duration: <strong>{q.duration_minutes}m</strong>
                </p>
              </div>
              <div className="mt-4 pt-3 border-t flex items-center justify-between">
                {q.my_attempts?.length > 0 ? (
                  <span className="text-xs font-semibold text-emerald-700">
                    Best Score: {Math.max(...q.my_attempts.map((a) => a.score))} / {q.total_marks}
                  </span>
                ) : (
                  <span className="text-xs text-slate-400">Not attempted yet</span>
                )}

                {user?.role === "student" && (
                  <button
                    onClick={() => { setResult(null); setSelected({}); setActiveQuiz(q); }}
                    className="px-3 py-1.5 bg-indigo-600 text-white text-xs font-semibold rounded-lg"
                  >
                    Start Quiz
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
