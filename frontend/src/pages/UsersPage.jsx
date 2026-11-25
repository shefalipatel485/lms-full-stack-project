import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function UsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");

  const loadUsers = () => {
    api.get("/api/users", { params: search ? { search } : {} }).then((res) => setUsers(res.data));
  };

  useEffect(() => {
    loadUsers();
  }, [search]);

  const toggleStatus = async (u) => {
    await api.put(`/api/users/${u.id}`, { is_active: !u.is_active });
    loadUsers();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">User & Student Directory</h1>
          <p className="text-sm text-slate-500">Manage institute accounts, roles, and active status</p>
        </div>
        <input
          type="text"
          placeholder="Search name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white"
        />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 border-b text-slate-600">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              {user?.role === "admin" && <th className="px-4 py-3">Action</th>}
            </tr>
          </thead>
          <tbody className="divide-y">
            {users.map((u) => (
              <tr key={u.id}>
                <td className="px-4 py-3 font-medium">{u.full_name}</td>
                <td className="px-4 py-3 text-slate-600">{u.email}</td>
                <td className="px-4 py-3 capitalize">{u.role}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${u.is_active ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
                    {u.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                {user?.role === "admin" && (
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggleStatus(u)}
                      className="text-xs font-semibold text-indigo-600 hover:underline"
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
