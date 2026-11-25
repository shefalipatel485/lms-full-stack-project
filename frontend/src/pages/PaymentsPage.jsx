import React, { useEffect, useState } from "react";
import api from "../services/api";
import { formatCurrencyINR, formatDate } from "../utils/formatters";

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    api.get("/api/payments").then((res) => setPayments(res.data));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Fee Records & Receipts</h1>
        <p className="text-sm text-slate-500">Course fee installments, balances, and payment history</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b text-slate-600">
              <tr>
                <th className="px-4 py-3">Receipt #</th>
                <th className="px-4 py-3">Student</th>
                <th className="px-4 py-3">Course</th>
                <th className="px-4 py-3">Total Fee</th>
                <th className="px-4 py-3">Paid</th>
                <th className="px-4 py-3">Pending</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {payments.map((p) => (
                <tr key={p.id}>
                  <td className="px-4 py-3 font-mono text-xs font-semibold">{p.receipt_number}</td>
                  <td className="px-4 py-3">{p.student_name}</td>
                  <td className="px-4 py-3">{p.course_title}</td>
                  <td className="px-4 py-3">{formatCurrencyINR(p.total_fee)}</td>
                  <td className="px-4 py-3 text-emerald-700 font-semibold">{formatCurrencyINR(p.amount_paid)}</td>
                  <td className="px-4 py-3 text-amber-700 font-semibold">{formatCurrencyINR(p.pending_amount)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${p.status === "Paid" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs">{formatDate(p.payment_date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
