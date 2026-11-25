import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = sessionStorage.getItem("lms_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = sessionStorage.getItem("lms_token");
    if (token && !user) {
      api.get("/api/auth/me")
        .then((res) => {
          setUser(res.data);
          sessionStorage.setItem("lms_user", JSON.stringify(res.data));
        })
        .catch(() => logout());
    }
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", { email, password });
      sessionStorage.setItem("lms_token", res.data.access_token);
      sessionStorage.setItem("lms_user", JSON.stringify(res.data.user));
      setUser(res.data.user);
      return res.data.user;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    sessionStorage.removeItem("lms_token");
    sessionStorage.removeItem("lms_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
