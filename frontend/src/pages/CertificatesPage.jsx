import React, { useEffect, useState } from "react";
import api, { API_BASE_URL } from "../services/api";
import { formatDate } from "../utils/formatters";
import { Award, Download, ShieldCheck } from "lucide-react";

export default function CertificatesPage() {
  const [certs, setCerts] = useState([]);
  const [verifyId, setVerifyId] = useState("CERT-LMS-2026-8841");
  const [verifyResult, setVerifyResult] = useState(null);
  const [verifyErr, setVerifyErr] = useState("");

  useEffect(() => {
    api.get("/api/certificates").then((res) => setCerts(res.data));
  }, []);

  const handleVerify = async (e) => {
    e.preventDefault();
    setVerifyErr("");
    setVerifyResult(null);
    try {
      const res = await api.get(`/api/certificates/verify/${verifyId}`);
      setVerifyResult(res.data);
    } catch {
      setVerifyErr("Certificate ID not found in institute registry.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Certificates & Verification</h1>
        <p className="text-sm text-slate-500">Download official course completion PDFs and verify credentials</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {certs.map((c) => (
          <div key={c.id} className="bg-white rounded-xl border border-slate-200 p-5 flex items-center justify-between">
            <div className="flex items-start gap-3">
              <div className="p-2.5 bg-amber-50 text-amber-600 rounded-lg">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900">{c.course_title}</h3>
                <p className="text-xs text-slate-500 mt-0.5">Issued to: {c.student_name} on {formatDate(c.issued_date)}</p>
                <p className="text-xs font-mono text-indigo-600 mt-1">{c.certificate_number}</p>
              </div>
            </div>
            <a
              href={`${API_BASE_URL}/api/certificates/${c.certificate_number}/download`}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-lg hover:bg-indigo-700"
            >
              <Download className="w-4 h-4" /> PDF
            </a>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 max-w-xl">
        <h2 className="font-bold text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-600" /> Verify Certificate Authenticity
        </h2>
        <form onSubmit={handleVerify} className="mt-3 flex gap-2">
          <input
            type="text"
            required
            value={verifyId}
            onChange={(e) => setVerifyId(e.target.value)}
            placeholder="Enter Certificate Number"
            className="flex-1 border rounded-lg px-3 py-2 text-sm font-mono"
          />
          <button type="submit" className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg">
            Verify
          </button>
        </form>
        {verifyResult && (
          <div className="mt-3 p-3 rounded-lg bg-emerald-50 text-emerald-800 text-sm">
            Verified Authentic: <strong>{verifyResult.student_name}</strong> completed <strong>{verifyResult.course_title}</strong> ({formatDate(verifyResult.issued_date)}).
          </div>
        )}
        {verifyErr && <p className="mt-3 text-sm text-rose-600">{verifyErr}</p>}
      </div>
    </div>
  );
}
